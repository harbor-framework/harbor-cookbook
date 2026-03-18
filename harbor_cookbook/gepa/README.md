# GEPA + Harbor: Agent Optimization on MedAgentBench

This example uses [GEPA](https://github.com/laude-institute/gepa)'s `optimize_anything` API to optimize an agent for [MedAgentBench](https://github.com/stanfordmlgroup/MedAgentBench) with [Harbor](https://github.com/harbor-framework/harbor).

## Prerequisites

Docker running and an `OPENAI_API_KEY` (for the codex agent and GEPA's reflection LLM).

## Quick start

```bash
uv run harbor_cookbook/gepa/optimize.py
```

See `--help` for options (agent, model, environment, worker count, iteration budget, etc.).

## Results

You should expect GEPA to roughly double accuracy within a few iterations — e.g. from ~28% to ~50% on a 32-task val set with codex/gpt-5-nano after 3 optimization loops.
