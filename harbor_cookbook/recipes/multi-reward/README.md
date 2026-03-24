# multi-reward

Demonstrates multiple verifiers writing independent rewards to `reward.json` instead of a single binary `reward.txt`. The agent's solution is scored separately for **correctness** and **performance**.

## Structure

```
multi-reward/
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

This recipe writes two reward dimensions (`correctness`, `performance`) to `reward.json`. Harbor's default `mean` metric only supports single-key rewards, so you must pass the included `config.yaml` which uses a custom per-dimension metric:

```bash
harbor run -p harbor_cookbook/recipes/multi-reward -c harbor_cookbook/recipes/multi-reward/config.yaml
```

To run a single trial without metrics (useful for quick iteration):

```bash
harbor trials start -p harbor_cookbook/recipes/multi-reward
```
