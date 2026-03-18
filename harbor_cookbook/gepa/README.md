# GEPA + Harbor: Agent Prompt Discovery on MedAgentBench

This example uses [GEPA](https://github.com/laude-institute/gepa)'s `optimize_anything` API to evolve agent prompts for [MedAgentBench](https://github.com/stanfordmlgroup/MedAgentBench), evaluated by [Harbor](https://github.com/harbor-framework/harbor) Trials.

## How it works

```
GEPA candidate (strategy prompt)
  → copy Harbor task dir, prepend candidate to instruction.md
    → Harbor Trial with real agent (claude-code)
      → Docker (prebuilt image: FHIR server + medagentbench_cli.py)
        → agent reads instruction.md, queries FHIR, writes answer.json
          → test.sh → verify.py checks answer → reward.txt (0/1)
  → read TrialResult.verifier_result.rewards → score for GEPA
```

GEPA evolves a strategy prompt that gets prepended to each task's `instruction.md`. The prompt guides the coding agent on how to interact with the FHIR server, structure queries, and format answers.

## Prerequisites

```bash
uv pip install harbor gepa
```

Docker running and an `OPENAI_API_KEY` (for the codex agent and GEPA's reflection LLM).

## Quick start

```bash
uv run python harbor_cookbook/gepa/optimize.py
```
