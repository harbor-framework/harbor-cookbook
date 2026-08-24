# /// script
# dependencies = ["mosaic-sandbox[harbor]>=0.11.1"]
# requires-python = ">=3.12"
# ///
"""Generate grouped Harbor rollouts with Mosaic or another provider."""

from __future__ import annotations

import argparse
import asyncio
import json
import time
from pathlib import Path

from mosaic_sandbox.integrations.harbor_rl import (
    MOSAIC_ENVIRONMENT_IMPORT_PATH,
    generate_rollouts,
    rollout_group_to_dict,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset", help="Harbor dataset name, such as terminal-bench@2.0"
    )
    parser.add_argument(
        "--task",
        action="append",
        type=Path,
        help="Local Harbor task directory; repeat for multiple tasks",
    )
    parser.add_argument("--group-size", type=int, default=4)
    parser.add_argument("--n-concurrent", type=int, default=4)
    parser.add_argument("--agent", default="terminus-2")
    parser.add_argument("--model", required=True)
    parser.add_argument("--env", default="mosaic")
    parser.add_argument("--jobs-dir", type=Path, default=Path("jobs"))
    parser.add_argument("--output", type=Path, default=Path("rollouts.json"))
    parser.add_argument(
        "--reward-only",
        action="store_true",
        help="Skip token extraction for evaluation-only runs",
    )
    args = parser.parse_args()
    if not args.dataset and not args.task:
        parser.error("one of --dataset or --task is required")

    environment_import_path = None
    environment_type = None
    if args.env == "mosaic":
        environment_import_path = MOSAIC_ENVIRONMENT_IMPORT_PATH
    elif args.env == "daytona":
        environment_type = "daytona"
    else:
        environment_import_path = args.env

    started = time.perf_counter()
    groups = asyncio.run(
        generate_rollouts(
            args.task,
            dataset=args.dataset,
            agent=args.agent,
            model=args.model,
            group_size=args.group_size,
            n_concurrent=args.n_concurrent,
            jobs_dir=args.jobs_dir,
            reward_only=args.reward_only,
            environment_import_path=environment_import_path,
            environment_type=environment_type,
        )
    )
    elapsed = time.perf_counter() - started

    args.output.write_text(
        json.dumps([rollout_group_to_dict(group) for group in groups], indent=2) + "\n"
    )
    for group in groups:
        print(f"{group.task_name}: {[attempt.reward for attempt in group.attempts]}")

    n_rollouts = sum(len(group) for group in groups)
    print(f"Rollouts: {n_rollouts}")
    print(
        f"Wall-clock: {elapsed:.3f}s\nRollouts/sec: {n_rollouts / elapsed:.3f}"
        if elapsed
        else "Wall-clock: 0.000s\nRollouts/sec: inf"
    )
    print(
        f"Mean per-trial wall time: {elapsed / n_rollouts:.3f}s"
        if n_rollouts
        else "Mean per-trial wall time: n/a"
    )
    print(f"Wrote grouped rollouts to {args.output}")


if __name__ == "__main__":
    main()
