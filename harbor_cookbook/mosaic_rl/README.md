# mosaic-rl

Grouped Harbor rollouts on Mosaic Sandbox using the released Harbor 0.22
`Job`/`JobConfig` API.

## Prerequisites

```bash
pip install 'mosaic-sandbox[harbor]'
mos login
```

You also need a model provider key. Set `MOSAIC_API_TOKEN` instead of using
`mos login` if preferred. A `DAYTONA_API_KEY` is needed only for the optional
comparison below.

## Quick start

```bash
uv run harbor_cookbook/mosaic_rl/rollout.py \
    --dataset terminal-bench@2.0 \
    --group-size 4 \
    --n-concurrent 16 \
    --agent terminus-2 \
    --model hosted_vllm/my-model
```

Use `--task ./path/to/task` instead of `--dataset`, repeating `--task` for
multiple local tasks. The script prints each task's `k` rewards and writes
grouped rollouts to `rollouts.json`. Token IDs and masks are required by
default; add `--reward-only` for evaluation-only runs.

## Why group rollouts on Mosaic?

A GRPO-style step samples `k` attempts for one task. Mosaic builds that task's
environment once into a content-addressed snapshot, then restores an isolated
sandbox for each attempt. The build cost is therefore amortised across the
group rather than paid once per attempt.

The script currently selects Mosaic through
`import_path="mosaic_sandbox.integrations.harbor:MosaicEnvironment"`, which
works with stock Harbor 0.22. Once the upstream provider lands, `--env mosaic`
will be available as a native Harbor environment selection.

This example intentionally targets the released Harbor `Job`/`JobConfig` API.
The sibling `harbor_rl` example targets the `harbor.rl` interface from open
upstream PR [#1291](https://github.com/harbor-framework/harbor/pull/1291);
the two examples use different APIs on purpose.

## Mosaic and Daytona comparison

The script accepts `--env mosaic`, `--env daytona`, or another Harbor
environment import path. Run both arms with the same task set, `k`, concurrency,
agent, and model:

```bash
uv run harbor_cookbook/mosaic_rl/rollout.py \
    --dataset terminal-bench@2.0 \
    --group-size 4 \
    --n-concurrent 16 \
    --agent terminus-2 \
    --model hosted_vllm/my-model \
    --env mosaic \
    --jobs-dir jobs/mosaic

DAYTONA_API_KEY=... uv run harbor_cookbook/mosaic_rl/rollout.py \
    --dataset terminal-bench@2.0 \
    --group-size 4 \
    --n-concurrent 16 \
    --agent terminus-2 \
    --model hosted_vllm/my-model \
    --env daytona \
    --jobs-dir jobs/daytona
```

Record wall-clock time, rollouts per second, and mean per-trial wall time from
each run. Separately record the first-attempt cost and the subsequent-attempt
cost: use a fresh snapshot/task for the first-attempt observation and inspect
the provider and trial timestamps for the grouped run so the one-time build
and per-attempt restore costs remain visible. Do not compare runs with
different task content, model, agent, `k`, or concurrency.
