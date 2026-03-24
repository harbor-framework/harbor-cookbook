# /// script
# dependencies = ["harbor", "gepa"]
# requires-python = ">=3.12"
# ///
"""GEPA prompt optimization for MedAgentBench.

Evolves the agent prompt template that wraps each task's instruction.md via
Harbor's prompt_template_path mechanism.  Evaluated by running a coding
agent (codex by default) on medagentbench@1.0 Harbor Trials.
"""

import argparse
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
    DEFAULT_ENVIRONMENT,
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
    "Optimize a prompt template that wraps medical task instructions. "
    "The prompt guides a coding agent on how to query a FHIR server and "
    "answer clinical EHR questions. "
)

BACKGROUND = (
    "The medical tasks span 10 categories: patient lookup, lab results, "
    "vitals, medications, conditions, procedures, service requests, and "
    "clinical reasoning. Each task runs with a FHIR "
    "server at http://localhost:8080/fhir/.\n\n"
    "The agent receives the task's instruction.md wrapped by the prompt "
    "template being optimized. The agent must query the FHIR server "
    "and write the answer to /workspace/answer.json.\n\n"
    "The prompt template should help the agent approach tasks more effectively "
    "— better FHIR query patterns, answer formatting, error recovery, etc."
)


# Global state set by CLI args so the evaluate callback can access them.
_agent_name: str = DEFAULT_AGENT
_model_name: str = DEFAULT_MODEL
_environment: str = DEFAULT_ENVIRONMENT


def evaluate(candidate, example):
    """Run one Harbor trial and return (score, side_info)."""
    task_id = example.id.name
    log.info("Evaluating %s ...", task_id)

    result = run_trial(
        candidate,
        example.downloaded_path,
        agent_name=_agent_name,
        model_name=_model_name,
        environment_type=_environment,
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


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)

    # Harbor trial settings
    g = p.add_argument_group("Harbor trials")
    g.add_argument(
        "--agent",
        default=DEFAULT_AGENT,
        help="Harbor agent name (default: %(default)s)",
    )
    g.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="LLM model for the agent (default: %(default)s)",
    )
    g.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Concurrent Harbor trials (default: %(default)s)",
    )
    g.add_argument(
        "--environment",
        default=DEFAULT_ENVIRONMENT,
        help="Harbor environment type (default: %(default)s)",
    )

    # GEPA settings
    g = p.add_argument_group("GEPA optimization")
    g.add_argument(
        "--max-evals",
        type=int,
        default=100,
        help="Total evaluation budget (default: %(default)s)",
    )
    g.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help="Max optimization iterations (default: unlimited)",
    )
    g.add_argument(
        "--subsample-size",
        type=int,
        default=3,
        help="Train tasks per iteration subsample (default: %(default)s)",
    )
    g.add_argument(
        "--reflection-model",
        default="openai/gpt-5.4",
        help="LLM for GEPA reflection (default: %(default)s)",
    )
    g.add_argument(
        "--max-val",
        type=int,
        default=None,
        help="Cap the val set size (default: use full val set)",
    )
    g.add_argument(
        "--output-dir",
        default="outputs/medagentbench",
        help="Directory for results (default: %(default)s)",
    )

    return p.parse_args()


def main():
    global _agent_name, _model_name, _environment

    args = parse_args()
    _agent_name = args.agent
    _model_name = args.model
    _environment = args.environment

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%H:%M:%S",
    )

    log.info("Downloading medagentbench@1.0 dataset ...")
    items = download_tasks()
    train, val = split_tasks(items, max_val=args.max_val)
    log.info("Dataset ready — %d train, %d val tasks", len(train), len(val))

    log.info(
        "Starting GEPA optimization (agent=%s, model=%s, workers=%d, evals=%d)",
        _agent_name,
        _model_name,
        args.max_workers,
        args.max_evals,
    )
    result = optimize_anything(
        seed_candidate=SEED,
        evaluator=evaluate,
        dataset=train,
        valset=val,
        objective=OBJECTIVE,
        background=BACKGROUND,
        config=GEPAConfig(
            engine=EngineConfig(
                max_metric_calls=args.max_evals,
                max_candidate_proposals=args.max_iterations,
                max_workers=args.max_workers,
                run_dir=args.output_dir,
            ),
            reflection=ReflectionConfig(
                reflection_lm=args.reflection_model,
                reflection_minibatch_size=args.subsample_size,
            ),
        ),
    )

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "best_prompt.txt").write_text(result.best_candidate)

    best_score = result.val_aggregate_scores[result.best_idx]
    log.info("Best val score: %.3f", best_score)
    log.info("Best prompt written to %s", out_dir / "best_prompt.txt")


if __name__ == "__main__":
    main()
