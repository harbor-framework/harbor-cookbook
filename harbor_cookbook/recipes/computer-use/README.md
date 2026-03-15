# computer-use

Computer-use task with a virtual desktop and MCP tools for screenshots, clicks, typing, and key presses. Inspired by the [Harbor OSWorld adapter](https://github.com/Mascobot/harbor/tree/main/adapters/osworld).

## Structure

```
computer-use/
├── README.md
├── task.toml                     # MCP server declared under [[environment.mcp_servers]]
├── instruction.md                # Agent prompt
├── environment/
│   ├── Dockerfile                # Agent container
│   ├── docker-compose.yaml       # Adds desktop service alongside main
│   └── desktop/                  # Virtual desktop + FastMCP server
│       ├── Dockerfile
│       ├── entrypoint.sh         # Starts Xvfb → fluxbox → xterm → MCP server
│       └── server.py             # screenshot, click, type_text, press_key
├── tests/
│   ├── test.sh                   # Verifier entrypoint
│   └── test_outputs.py           # Pytest assertions
└── solution/
    └── solve.sh                  # Reference solution
```

## How it works

A companion container runs a virtual desktop (Xvfb + Fluxbox + xterm) alongside a FastMCP server that exposes `screenshot`, `click`, `type_text`, and `press_key` tools. The desktop and MCP server share a container because the tools need direct access to the X display.

The agent takes a screenshot, reads a secret code from the image (using vision), and writes it to a file. This demonstrates how to build tasks that require visual understanding and desktop interaction.

The `[[environment.mcp_servers]]` section in `task.toml` declares the MCP server. Harbor passes this config to the agent at startup.

## Run

```bash
harbor run -p harbor_cookbook/recipes/computer-use --agent claude-code --model anthropic/claude-sonnet-4-6
```

## Limitations

Multi-container tasks require the **docker** environment provider because they rely on Docker Compose networking. They are not supported on cloud providers (Daytona, Modal, E2B, etc.).
