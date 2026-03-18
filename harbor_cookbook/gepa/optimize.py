"""Discover medical agent prompts with GEPA on MedAgentBench.

GEPA evolves a strategy prompt that gets prepended to each task's
``instruction.md``.  Every evaluation runs as a Harbor Trial using a real
coding agent (claude-code by default) on the ``medagentbench@1.0`` registry
dataset (prebuilt Docker image with FHIR server, official grading).
"""

from pathlib import Path

import gepa.optimize_anything as oa
from gepa.optimize_anything import (
    EngineConfig,
    GEPAConfig,
    ReflectionConfig,
    optimize_anything,
)

from harbor_cookbook.gepa.utils import (
    DEFAULT_AGENT,
    DEFAULT_MODEL,
    download_tasks,
    run_trial,
    split_tasks,
)

# ---------------------------------------------------------------------------
# Seed prompt — prepended to each task's instruction.md.
# Gives the agent high-level strategy for MedAgentBench tasks.
# ---------------------------------------------------------------------------
SEED = """\
Answer the clinical question by querying the FHIR server. Return exact values \
from the data, not explanations. Use `_sort=-date&_count=1` for "most recent" \
queries. Call `medagentbench_cli.py finish '[...]'` with a JSON list as the \
final step.
"""

OBJECTIVE = (
    "Optimize a strategy prompt that gets prepended to MedAgentBench task "
    "instructions. The prompt guides a coding agent on how to "
    "interact with a FHIR server and answer clinical EHR questions. "
    "Graded by the official MedAgentBench verifier (binary: 1=correct, 0=wrong)."
)

BACKGROUND = (
    "MedAgentBench tasks span 10 categories: patient lookup, lab results, "
    "vitals, medications, conditions, procedures, service requests, and "
    "clinical reasoning. Each task runs in a Docker container with a FHIR "
    "server at http://localhost:8080/fhir/.\n\n"
    "The agent receives the task's instruction.md (with question, context, "
    "FHIR server URL, CLI usage, and output format) prepended with the "
    "strategy prompt being optimized. The agent must query the FHIR server "
    "and write the answer to /workspace/answer.json.\n\n"
    "The strategy prompt should help the agent approach tasks more effectively "
    "— better FHIR query patterns, answer formatting, error recovery, etc."
)


def evaluate(candidate, example):
    """GEPA evaluator: run candidate prompt in a Harbor trial for one task."""
    task_id = example.id.name
    result = run_trial(
        candidate,
        example.downloaded_path,
        agent_name=DEFAULT_AGENT,
        model_name=DEFAULT_MODEL,
    )
    score = result["reward"]

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
    items = download_tasks()
    train, val = split_tasks(items)

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
    print(f"\nBest val score: {best_score:.3f}")
    print(f"Best prompt written to {out_dir / 'best_prompt.txt'}")


if __name__ == "__main__":
    main()
