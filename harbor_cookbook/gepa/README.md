# GEPA + Harbor: Agent Architecture Discovery on MedAgentBench

This example uses [GEPA](https://github.com/laude-institute/gepa)'s `optimize_anything` API to evolve agent code for [MedAgentBench](https://github.com/stanfordmlgroup/MedAgentBench), evaluated by [Harbor](https://github.com/harbor-framework/harbor) Trials.

## How it works

```
GEPA candidate (solve() function)
  → copy Harbor task dir, inject candidate into solve.sh
    → Harbor Trial with OracleAgent
      → Docker (prebuilt image: FHIR server + medagentbench_cli.py)
        → solve.sh → candidate calls LLM + FHIR APIs → answer.json
          → test.sh → verify.py checks answer → reward.txt (0/1)
  → read TrialResult.verifier_result.rewards → score for GEPA
```

GEPA evolves a `solve()` function that performs multi-turn FHIR API interactions to answer clinical EHR questions. The seed is a naive loop that prompts an LLM, parses GET/POST/FINISH actions, and executes them. GEPA discovers better prompting strategies, smarter FHIR query patterns, and more robust answer formatting.

The candidate `solve()` function receives helper functions:

- `fhir_get(url)` — GET a FHIR resource
- `fhir_post(url, payload)` — POST to a FHIR endpoint
- `finish(result_list)` — write the final answer
- `llm(prompt)` — call an LLM for reasoning

## Dataset split

300 tasks (10 types × 30 instances). Stratified split:

- **Train**: indices 1–20 per type (200 tasks)
- **Val**: indices 21–30 per type (100 tasks)

## Prerequisites

```bash
uv pip install harbor gepa litellm
```

You also need Docker running, an `OPENAI_API_KEY` set (for the candidate's LLM calls and GEPA's reflection LLM).

## Quick start

```bash
uv run python harbor_cookbook/gepa/optimize.py
```

The first trial takes several minutes (Docker image pull + FHIR server startup). Subsequent trials reuse the cached image.

## Running the full benchmark standalone

```bash
harbor run -d medagentbench@1.0 -a claude-code -m anthropic/claude-sonnet-4-6
```
