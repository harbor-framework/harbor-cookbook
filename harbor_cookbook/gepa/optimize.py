# /// script
# dependencies = ["harbor", "gepa"]
# requires-python = ">=3.12"
# ///
"""GEPA prompt optimization for MedAgentBench.

Evolves a prompt template that wraps each task's instruction.md via
Harbor's prompt_template_path mechanism.  Evaluated by running a coding
agent (codex by default) on medagentbench@1.0 Harbor Trials.
"""

import logging
from pathlib import Path

import gepa.optimize_anything as oa
from gepa.optimize_anything import (
    EngineConfig,
    GEPAConfig,
    ReflectionConfig,
    optimize_anything,
)

from utils import (
    DEFAULT_AGENT,
    DEFAULT_MODEL,
    download_tasks,
    run_trial,
    split_tasks,
)

log = logging.getLogger(__name__)

SEED = """\
Answer the clinical question by querying the FHIR server. Return exact values \
from the data, not explanations. Use `_sort=-date&_count=1` for "most recent" \
queries. Call `medagentbench_cli.py finish '[...]'` with a JSON list as the \
final step.
"""

OBJECTIVE = (
    "Optimize a prompt template that wraps MedAgentBench task instructions. "
    "The prompt guides a coding agent on how to query a FHIR server and "
    "answer clinical EHR questions. "
    "Graded by the official MedAgentBench verifier (binary: 1=correct, 0=wrong)."
)

BACKGROUND = (
    "MedAgentBench tasks span 10 categories: patient lookup, lab results, "
    "vitals, medications, conditions, procedures, service requests, and "
    "clinical reasoning. Each task runs in a Docker container with a FHIR "
    "server at http://localhost:8080/fhir/.\n\n"
    "The agent receives the task's instruction.md wrapped by the prompt "
    "template being optimized. The agent must query the FHIR server "
    "and write the answer to /workspace/answer.json.\n\n"
    "The prompt template should help the agent approach tasks more effectively "
    "— better FHIR query patterns, answer formatting, error recovery, etc."
)


def evaluate(candidate, example):
    """Run one Harbor trial and return (score, side_info)."""
    task_id = example.id.name
    log.info("Evaluating %s ...", task_id)

    result = run_trial(
        candidate,
        example.downloaded_path,
        agent_name=DEFAULT_AGENT,
        model_name=DEFAULT_MODEL,
    )
    score = result["reward"]

    if result["error"]:
        log.warning("[%s] reward=%s  error=%s", task_id, score, result["error"])
    else:
        log.info("[%s] reward=%s", task_id, score)

    summary = f"[{task_id}] reward={score}"
    if result["error"]:
        summary += f" error={result['error']}"
    elif result["verifier_output"]:
        summary += f" verifier={result['verifier_output']}"
    oa.log(summary)

    return score, {
        "task_id": task_id,
        "Verifier": result["verifier_output"],
        "Agent Trajectory": result["agent_output"],
        "Error": result["error"] or "",
    }


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%H:%M:%S",
    )

    log.info("Downloading medagentbench@1.0 dataset ...")
    items = download_tasks()
    train, val = split_tasks(items)
    log.info("Dataset ready — %d train, %d val tasks", len(train), len(val))

    log.info("Starting GEPA optimization (agent=%s, model=%s)", DEFAULT_AGENT, DEFAULT_MODEL)
    result = optimize_anything(
        seed_candidate=SEED,
        evaluator=evaluate,
        dataset=train,
        valset=val,
        objective=OBJECTIVE,
        background=BACKGROUND,
        config=GEPAConfig(
            engine=EngineConfig(
                max_metric_calls=100,
                max_workers=4,
                run_dir="outputs/medagentbench",
            ),
            reflection=ReflectionConfig(
                reflection_lm="openai/gpt-5.4",
            ),
        ),
    )

    out_dir = Path("outputs/medagentbench")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "best_prompt.txt").write_text(result.best_candidate)

    best_score = result.val_aggregate_scores[result.best_idx]
    log.info("Best val score: %.3f", best_score)
    log.info("Best prompt written to %s", out_dir / "best_prompt.txt")


if __name__ == "__main__":
    main()
