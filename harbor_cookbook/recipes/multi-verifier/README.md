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
# Single trial (task validation)
harbor trials start -p harbor_cookbook/recipes/multi-verifier

# Job with per-dimension metrics
harbor run -p harbor_cookbook/recipes/multi-verifier -c harbor_cookbook/recipes/multi-verifier/config.yaml -a claude-code -m anthropic/claude-sonnet-4-6
```

The `config.yaml` uses a custom `uv_script` metric that computes mean reward per dimension, since the default `mean` metric only supports single-key rewards.
