# multi-container

Docker Compose task with an additional service the agent interacts with over the Docker network.

## Structure

```
multi-container/
├── README.md
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

When `environment/docker-compose.yaml` is present, Harbor merges it on top of its base Compose config. The `main` service (agent container) is configured automatically — you only define overrides and additional services.

Here, `docker-compose.yaml` adds an `api-server` service with a healthcheck. The `main` service uses `depends_on` to wait for it. The agent reaches the API at `http://api-server:5000` via the Docker network — no port mapping needed.

## Run

```bash
harbor run -p harbor_cookbook/recipes/multi-container --agent claude-code --model anthropic/claude-sonnet-4-6
```

## Limitations

Multi-container tasks require the **docker** environment provider because they rely on Docker Compose networking. They are not supported on some of the cloud providers in Harbor (Modal, E2B, etc.).
