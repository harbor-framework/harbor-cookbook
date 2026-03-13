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

## How it works

The agent runs inside an `ubuntu:24.04` container and receives `instruction.md` — create a file with specific content. Harbor mounts the agent's working directory at `/app`.

After the agent finishes (or times out), Harbor runs `tests/test.sh` in a separate verifier container. The test script installs pytest, runs `test_state.py` against `/app`, and writes `1` (pass) or `0` (fail) to `/logs/verifier/reward.txt`.

## Run

```bash
harbor run -p harbor_cookbook/recipes/simple-task --agent claude-code --model anthropic/claude-sonnet-4-6
```
