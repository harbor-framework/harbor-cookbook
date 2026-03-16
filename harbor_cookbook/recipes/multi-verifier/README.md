# multi-verifier

Demonstrates multi-dimensional verification using `reward.json` instead of binary `reward.txt`. The agent's solution is scored on two independent dimensions: **correctness** and **performance**.

## Structure

```
multi-verifier/
├── README.md
├── task.toml              # Timeouts and resource limits
├── instruction.md         # What the agent should do
├── environment/
│   └── Dockerfile         # Agent container (ubuntu:24.04 + Python 3)
├── tests/
│   ├── test.sh            # Runs both test suites, writes reward.json
│   ├── test_correctness.py
│   └── test_performance.py
└── solution/
    └── solve.sh           # Reference solution
```

## Run

```bash
harbor run -p harbor_cookbook/recipes/multi-verifier --agent claude-code --model anthropic/claude-sonnet-4-6
```
