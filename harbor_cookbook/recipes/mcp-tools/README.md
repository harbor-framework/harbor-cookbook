# mcp-tools

Giving agents access to custom MCP tools via a FastMCP server running in a companion container.

## Structure

```
mcp-tools/
├── README.md
├── task.toml                  # MCP server declared under [[environment.mcp_servers]]
├── instruction.md             # Agent prompt
├── environment/
│   ├── Dockerfile             # Agent container
│   ├── docker-compose.yaml    # Adds mcp-server service alongside main
│   └── mcp-server/            # FastMCP server (streamable-http)
│       ├── Dockerfile
│       └── server.py
├── tests/
│   ├── test.sh                # Verifier entrypoint
│   └── test_outputs.py        # Pytest assertions
└── solution/
    └── solve.sh               # Reference solution
```

## How it works

The `[[environment.mcp_servers]]` table in `task.toml` tells Harbor to pass the server config to the agent. Each agent decides how to consume it (e.g., Claude Code writes it to `~/.claude.json`).

The MCP server runs in a separate container and exposes tools over `streamable-http`. The agent discovers and calls these tools through its native MCP support.

## Run

```bash
harbor run -p harbor_cookbook/recipes/mcp-tools --agent claude-code --model anthropic/claude-sonnet-4-6
```

## Limitations

Multi-container tasks require the **docker** environment provider because they rely on Docker Compose networking. They are not supported on cloud providers (Daytona, Modal, E2B, etc.).
