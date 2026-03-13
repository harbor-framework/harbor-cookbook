# simple-task

A minimal Harbor task showing the basic directory structure: Dockerfile, instruction, test, and solution.

## Structure

```
simple-task/
├── README.md
├── task.toml              # Timeouts and resource limits
├── instruction.md         # What the agent should do
├── environment/
│   └── Dockerfile         # Agent container (ubuntu:24.04)
├── tests/
│   ├── test.sh            # Installs pytest, runs tests, writes reward
│   └── test_state.py      # Pytest assertions
└── solution/
    └── solve.sh           # Reference solution
```

## Run

```bash
harbor run -p harbor_cookbook/recipes/simple-task --agent claude-code --model anthropic/claude-sonnet-4-6
```
