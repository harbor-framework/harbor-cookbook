# GEPA + Harbor: Agent Optimization on MedAgentBench

This example uses [GEPA](https://github.com/laude-institute/gepa)'s `optimize_anything` API to optimize an agent for [MedAgentBench](https://github.com/stanfordmlgroup/MedAgentBench) with [Harbor](https://github.com/harbor-framework/harbor).

## Prerequisites

Docker running and an `OPENAI_API_KEY` (for the codex agent and GEPA's reflection LLM).

## Quick start

```bash
uv run harbor_cookbook/gepa/optimize.py
```
