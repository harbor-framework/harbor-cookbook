"""Utilities for downloading MedAgentBench tasks and running Harbor trials."""

import asyncio
import json
import os
import re
import shutil
import tempfile
from collections import defaultdict
from pathlib import Path

from harbor.models.trial.config import (
    AgentConfig,
    EnvironmentConfig,
    TaskConfig,
    TrialConfig,
    VerifierConfig,
)
from harbor.registry.client import RegistryClientFactory
from harbor.trial.trial import Trial

# ---------------------------------------------------------------------------
# FHIR wait script — identical to the upstream MedAgentBench solve.sh preamble
# ---------------------------------------------------------------------------
_FHIR_WAIT = r"""
FHIR_METADATA_URL="http://127.0.0.1:8080/fhir/metadata"
FHIR_STARTUP_TIMEOUT_SEC="${FHIR_STARTUP_TIMEOUT_SEC:-900}"
FHIR_POLL_INTERVAL_SEC="${FHIR_POLL_INTERVAL_SEC:-2}"
FHIR_START_SCRIPT="/etc/profile.d/medagentbench_fhir.sh"

fhir_http_code() {
  curl -sS --connect-timeout 1 --max-time 10 -o /dev/null -w "%{http_code}" \
    "$FHIR_METADATA_URL" 2>/dev/null || echo "000"
}
start_fhir_best_effort() {
  if [ -f "$FHIR_START_SCRIPT" ]; then
    bash "$FHIR_START_SCRIPT" >/dev/null 2>&1 || true
  fi
}
start_fhir_best_effort
ready=0; last_code="000"
deadline=$((SECONDS + FHIR_STARTUP_TIMEOUT_SEC))
while [ "$SECONDS" -lt "$deadline" ]; do
  last_code="$(fhir_http_code)"
  if [ "$last_code" = "200" ]; then ready=1; break; fi
  start_fhir_best_effort
  sleep "$FHIR_POLL_INTERVAL_SEC"
done
if [ "$ready" -ne 1 ]; then
  echo "FHIR not ready (last_http_code=${last_code})" >&2; exit 1
fi
""".strip()

# ---------------------------------------------------------------------------
# Runner script — mirrors the official MedAgentBench agent protocol.
#
# The candidate's solve() receives (question, context, fhir_base, functions)
# and returns (result_list, history).  The runner handles FHIR execution and
# answer submission, keeping the candidate focused on the decision logic.
# ---------------------------------------------------------------------------
_RUNNER_PY = r'''#!/usr/bin/env python3
"""Run the candidate solve() and write /workspace/answer.json."""

import json
import subprocess
import sys
from pathlib import Path

metadata = json.loads(Path("/solution/task_metadata.json").read_text())
task_id = metadata.get("task_id", "unknown")
question = metadata.get("question", "")
context = metadata.get("context", "")
fhir_base = metadata.get("fhir_api_base", "http://localhost:8080/fhir/")
functions = Path("/workspace/funcs_v1.json").read_text()

print(f"=== {task_id} ===", flush=True)

sys.path.insert(0, "/workspace")
from agent import solve  # noqa: E402

result_list, history = solve(
    question=question,
    context=context,
    fhir_base=fhir_base,
    functions=functions,
)

# Write answer
subprocess.run(
    ["/usr/local/bin/medagentbench_cli.py", "finish", json.dumps(result_list)],
    capture_output=True, text=True,
)
print(f"Answer: {json.dumps(result_list)}", flush=True)
'''.strip()

# FHIR function definitions from the official MedAgentBench repo.
_FUNCS_V1_PATH = Path(__file__).parent / "funcs_v1.json"


def download_tasks():
    """Download medagentbench@1.0 tasks, return list of DownloadedDatasetItems."""
    client = RegistryClientFactory.create()
    return client.download_dataset("medagentbench", version="1.0")


def split_tasks(items):
    """Stratified split: train (indices 1-20), val (21-30) per task type.

    Task IDs follow the pattern taskX_Y where X is type (1-10) and Y is
    the instance number (1-30).  Returns (train, val).
    """
    by_type = defaultdict(list)
    for item in items:
        name = item.id.name  # e.g. "task1_5"
        parts = name.rsplit("_", 1)
        by_type[parts[0]].append((int(parts[1]), item))

    train, val = [], []
    for task_type in sorted(by_type):
        for idx, item in sorted(by_type[task_type]):
            (train if idx <= 20 else val).append(item)
    return train, val


def _parse_instruction_md(text: str) -> tuple[str, str]:
    """Extract question and context from the Harbor instruction.md template."""
    question = ""
    context = ""
    m = re.search(r"## Original Instruction\n(.+?)(?=\n## )", text, re.DOTALL)
    if m:
        question = m.group(1).strip()
    m = re.search(r"## Context\n(.+?)(?=\n## )", text, re.DOTALL)
    if m:
        ctx = m.group(1).strip()
        if ctx != "(none)":
            context = ctx
    return question, context


def _inject_metadata(task_dir: Path) -> None:
    """Add question/context from instruction.md to solution/task_metadata.json."""
    instruction_path = task_dir / "instruction.md"
    meta_path = task_dir / "solution" / "task_metadata.json"
    if not instruction_path.exists() or not meta_path.exists():
        return
    meta = json.loads(meta_path.read_text())
    question, context = _parse_instruction_md(instruction_path.read_text())
    meta["question"] = question
    meta["context"] = context
    meta_path.write_text(json.dumps(meta, indent=2))


def make_solve_sh(candidate_code: str, env: dict[str, str] | None = None) -> str:
    """Generate solve.sh that waits for FHIR, writes candidate + runner, runs it."""
    env_exports = ""
    if env:
        for key, val in env.items():
            env_exports += f"export {key}='{val}'\n"
        env_exports += "\n"

    # Bundle FHIR function definitions
    funcs_json = _FUNCS_V1_PATH.read_text() if _FUNCS_V1_PATH.exists() else "[]"

    return (
        "#!/bin/bash\nset -euo pipefail\n\n"
        + env_exports
        + _FHIR_WAIT
        + "\n\n# Install litellm\npip install --quiet litellm 2>/dev/null\n\n"
        + "cat > /workspace/funcs_v1.json << 'GEPA_FUNCS_EOF'\n"
        + funcs_json
        + "\nGEPA_FUNCS_EOF\n\n"
        + "cat > /workspace/agent.py << 'GEPA_AGENT_EOF'\n"
        + candidate_code
        + "\nGEPA_AGENT_EOF\n\n"
        + "cat > /workspace/runner.py << 'GEPA_RUNNER_EOF'\n"
        + _RUNNER_PY
        + "\nGEPA_RUNNER_EOF\n\n"
        + "python3 /workspace/runner.py\n"
    )


def _read_trial_file(trials_dir: Path, relative: str, limit: int = 3000) -> str:
    """Read a file from the trial output directory, truncating to limit chars."""
    for trial_dir in trials_dir.iterdir():
        path = trial_dir / relative
        if path.is_file():
            text = path.read_text(errors="replace")
            if len(text) > limit:
                return text[:limit] + f"\n... (truncated, {len(text)} total chars)"
            return text
    return ""


def run_trial(candidate_code: str, task_path: Path) -> dict:
    """Copy task dir, inject candidate into solve.sh, run Harbor Trial."""
    tmp = Path(tempfile.mkdtemp())
    try:
        task_dir = tmp / "task"
        shutil.copytree(task_path, task_dir, dirs_exist_ok=True)

        _inject_metadata(task_dir)

        # Forward API keys so the candidate can call LLMs inside the container
        env = {}
        for key in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY"):
            if key in os.environ:
                env[key] = os.environ[key]

        solve_sh = task_dir / "solution" / "solve.sh"
        solve_sh.write_text(make_solve_sh(candidate_code, env=env))
        solve_sh.chmod(0o755)

        config = TrialConfig(
            task=TaskConfig(path=task_dir),
            trials_dir=tmp / "trials",
            agent=AgentConfig(name="oracle"),
            environment=EnvironmentConfig(),
            verifier=VerifierConfig(),
        )
        result = asyncio.run(Trial(config).run())

        rewards = result.verifier_result.rewards if result.verifier_result else {}
        exc = result.exception_info

        # Read agent trajectory and verifier output before cleanup
        agent_output = _read_trial_file(tmp / "trials", "agent/oracle.txt")
        verifier_output = _read_trial_file(tmp / "trials", "verifier/test-output.txt")

        return {
            "reward": float(rewards.get("reward", 0)),
            "error": exc.exception_message if exc else None,
            "agent_output": agent_output,
            "verifier_output": verifier_output,
        }
    except Exception as e:
        return {
            "reward": 0.0,
            "error": str(e),
            "agent_output": "",
            "verifier_output": "",
        }
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
