# multi-container

Docker Compose task with an additional service the agent interacts with over the Docker network — no MCP involved.

## Limitations

Multi-container tasks require the **docker** environment provider because they rely on Docker Compose networking. They are not supported on cloud providers (Daytona, Modal, E2B, etc.).

## Structure

```
multi-container/
├── README.md
└── task/
    ├── task.toml                  # Task configuration
    ├── instruction.md             # Agent prompt
    ├── environment/
    │   ├── Dockerfile             # Agent container
    │   ├── docker-compose.yaml    # Adds api-server service alongside main
    │   └── api-server/            # A simple REST API
    │       ├── Dockerfile
    │       └── server.py
    ├── tests/
    │   ├── test.sh                # Verifier entrypoint
    │   └── test_outputs.py        # Pytest assertions
    └── solution/
        └── solve.sh               # Reference solution
```

## How it works

Harbor merges `docker-compose.yaml` on top of its base config. The `main` service (the agent container) is configured automatically — you only define overrides and additional services.

The `api-server` service exposes a REST API on port 5000. The agent can reach it at `http://api-server:5000` via Docker networking.

## Run

```bash
harbor run -p recipes/multi-container/task --agent claude-code --model anthropic/claude-sonnet-4-1
```
