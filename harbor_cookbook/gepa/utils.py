"""Utilities for downloading MedAgentBench tasks and running Harbor trials."""

import asyncio
import os
import shutil
import tempfile
from collections import defaultdict
from pathlib import Path

from harbor.models.environment_type import EnvironmentType
from harbor.models.trial.config import (
    AgentConfig,
    EnvironmentConfig,
    TaskConfig,
    TrialConfig,
    VerifierConfig,
)
from harbor.registry.client import RegistryClientFactory
from harbor.trial.trial import Trial

# Default agent, model, and environment for trials
DEFAULT_AGENT = "codex"
DEFAULT_MODEL = "openai/gpt-5-mini"
DEFAULT_ENVIRONMENT = EnvironmentType.DOCKER


def download_tasks():
    """Download medagentbench@1.0 tasks, return list of DownloadedDatasetItems."""
    client = RegistryClientFactory.create()
    return client.download_dataset("medagentbench", version="1.0")


def split_tasks(items, max_val: int | None = None):
    """Stratified split: train (indices 1-20), val (21-30) per task type.

    Task IDs follow the pattern taskX_Y where X is type (1-10) and Y is
    the instance number (1-30).  Returns (train, val).

    If *max_val* is set, the val set is truncated to that many tasks
    (still stratified — takes the first N per type evenly).
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

    if max_val is not None and len(val) > max_val:
        val = val[:max_val]

    return train, val


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


def run_trial(
    prompt: str,
    task_path: Path,
    agent_name: str = DEFAULT_AGENT,
    model_name: str = DEFAULT_MODEL,
    environment_type: EnvironmentType = DEFAULT_ENVIRONMENT,
) -> dict:
    """Run a Harbor Trial with the evolved prompt template."""
    tmp = Path(tempfile.mkdtemp())
    try:
        task_dir = tmp / "task"
        shutil.copytree(task_path, task_dir, dirs_exist_ok=True)

        # Write evolved prompt as a Jinja2 template that wraps instruction.md
        template_path = tmp / "prompt_template.txt"
        template_path.write_text(prompt + "\n\n{{ instruction }}")

        # Forward API keys so the agent can call LLMs inside the container
        agent_env = {}
        for key in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY"):
            if key in os.environ:
                agent_env[key] = os.environ[key]

        config = TrialConfig(
            task=TaskConfig(path=task_dir),
            trials_dir=tmp / "trials",
            agent=AgentConfig(
                name=agent_name,
                model_name=model_name,
                env=agent_env,
                kwargs={"prompt_template_path": str(template_path)},
            ),
            environment=EnvironmentConfig(type=environment_type),
            verifier=VerifierConfig(),
        )
        result = asyncio.run(Trial(config).run())

        rewards = result.verifier_result.rewards if result.verifier_result else {}
        exc = result.exception_info

        # Read agent trajectory and verifier output before cleanup
        agent_output = _read_trial_file(
            tmp / "trials", f"agent/{agent_name}.txt"
        )
        verifier_output = _read_trial_file(
            tmp / "trials", "verifier/test-output.txt"
        )

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
