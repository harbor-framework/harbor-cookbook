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

The `[[environment.mcp_servers]]` section in `task.toml` declares an MCP server. Harbor passes this config to the agent at startup — each agent decides how to consume it (e.g., Claude Code writes it to `~/.claude.json`).

The MCP server itself is a FastMCP app (`environment/mcp-server/server.py`) running in a companion container, exposed over `streamable-http` on port 8000. The agent discovers available tools and calls them through its native MCP support.

The `docker-compose.yaml` wires up the companion container the same way as in the multi-container recipe.

## Run

```bash
harbor run -p harbor_cookbook/recipes/mcp-tools --agent claude-code --model anthropic/claude-sonnet-4-6
```

## Limitations

Multi-container tasks require the **docker** environment provider because they rely on Docker Compose networking. They are not supported on cloud providers (Daytona, Modal, E2B, etc.).
