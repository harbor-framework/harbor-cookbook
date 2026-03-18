"""Utilities for downloading MedAgentBench tasks and running Harbor trials."""

import asyncio
import logging
import os
import shutil
import tempfile
import threading
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

log = logging.getLogger(__name__)

DEFAULT_AGENT = "codex"
DEFAULT_MODEL = "openai/gpt-5-nano"
DEFAULT_ENVIRONMENT = EnvironmentType.DOCKER

# Shared event loop so concurrent GEPA workers and async Harbor environments
# (e.g. Daytona) all share one loop.
_loop = asyncio.new_event_loop()
threading.Thread(target=_loop.run_forever, daemon=True).start()


def download_tasks():
    """Download medagentbench@1.0 tasks via the Harbor registry."""
    client = RegistryClientFactory.create()
    return client.download_dataset("medagentbench", version="1.0")


def split_tasks(items, max_val: int | None = None):
    """Stratified train/val split (indices 1-20 train, 21-30 val per type).

    If *max_val* is set the val set is capped at that size.
    """
    by_type = defaultdict(list)
    for item in items:
        name = item.id.name
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
    """Read a file from the trial output, truncating to *limit* chars."""
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
    """Run a single Harbor Trial with *prompt* as the prompt template."""
    tmp = Path(tempfile.mkdtemp())
    try:
        task_dir = tmp / "task"
        shutil.copytree(task_path, task_dir, dirs_exist_ok=True)

        template_path = tmp / "prompt_template.txt"
        template_path.write_text(prompt + "\n\n{{ instruction }}")

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

        log.debug("Starting trial for %s", task_dir.name)
        result = asyncio.run_coroutine_threadsafe(Trial(config).run(), _loop).result()

        rewards = result.verifier_result.rewards if result.verifier_result else {}
        exc = result.exception_info

        agent_output = _read_trial_file(tmp / "trials", f"agent/{agent_name}.txt")
        verifier_output = _read_trial_file(tmp / "trials", "verifier/test-output.txt")

        return {
            "reward": float(rewards.get("reward", 0)),
            "error": exc.exception_message if exc else None,
            "agent_output": agent_output,
            "verifier_output": verifier_output,
        }
    except Exception as e:
        log.error("Trial failed: %s", e)
        return {
            "reward": 0.0,
            "error": str(e),
            "agent_output": "",
            "verifier_output": "",
        }
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
