# multi-verifier

Demonstrates multiple verifiers writing independent rewards to `reward.json` instead of a single binary `reward.txt`. The agent's solution is scored separately for **correctness** and **performance**.

## Structure

```
multi-verifier/
├── README.md
├── task.toml              # Timeouts and resource limits
├── instruction.md         # What the agent should do
├── config.yaml            # Job config with per-dimension metrics
├── environment/
│   └── Dockerfile         # Agent container (ubuntu:24.04 + Python 3)
├── tests/
│   ├── test.sh            # Runs both test suites, writes reward.json
│   ├── test_correctness.py
│   └── test_performance.py
├── metrics/
│   └── per_dimension.py   # Custom metric: mean reward per dimension
└── solution/
    └── solve.sh           # Reference solution
```

## Run

```bash
harbor trials start -p harbor_cookbook/recipes/multi-verifier
```

## Metrics note

Harbor's default `mean` metric only supports single-key `reward.json`. Since this recipe writes two keys (`correctness`, `performance`), running `harbor run` requires a custom metric config:

```bash
harbor run -p harbor_cookbook/recipes/multi-verifier -c harbor_cookbook/recipes/multi-verifier/config.yaml
```

The included `config.yaml` uses a `uv-script` metric (`metrics/per_dimension.py`) that computes mean reward per dimension.
