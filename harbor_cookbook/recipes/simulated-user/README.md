# simulated-user

An MCP server that acts as a simulated user the agent must talk to. The agent discovers requirements through conversation, then builds what the user asks for.

## Limitations

Multi-container tasks require the **docker** environment provider because they rely on Docker Compose networking. They are not supported on cloud providers (Daytona, Modal, E2B, etc.).

## Structure

```
simulated-user/
├── README.md
└── task/
    ├── task.toml                  # MCP server declared under [[environment.mcp_servers]]
    ├── instruction.md             # Tells the agent to talk to the user
    ├── environment/
    │   ├── Dockerfile             # Agent container
    │   ├── docker-compose.yaml    # Adds user-server service alongside main
    │   └── user-server/           # Simulated user (FastMCP, streamable-http)
    │       ├── Dockerfile
    │       └── server.py
    ├── tests/
    │   ├── test.sh                # Verifier entrypoint
    │   └── test_outputs.py        # Checks output and that ask_user was called
    └── solution/
        └── solve.sh               # Reference solution
```

## How it works

The MCP server exposes a single `ask_user` tool. The "user" has a problem: they want a script that converts CSV to JSON. But the agent doesn't know this upfront — the instruction just says to talk to the user and build what they need.

The server is a simple state machine that reveals requirements incrementally:

1. First call: "I need a script that converts CSV files to JSON"
2. Second call: "The script should read from stdin and write to stdout"
3. Third call onwards: "That's everything, go ahead and build it"

Tests verify both the correct output and that the agent actually called `ask_user`.

## Run

```bash
harbor run -p recipes/simulated-user/task --agent claude-code --model anthropic/claude-sonnet-4-1
```
