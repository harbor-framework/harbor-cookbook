# computer-use

Multi-step computer-use task with a virtual desktop and MCP tools for screenshots, clicks, typing, and key presses. The agent must navigate a multi-step tkinter GUI challenge — clicking buttons, typing a passphrase, and reading a revealed secret code. Inspired by the [Harbor OSWorld adapter](https://github.com/Mascobot/harbor/tree/main/adapters/osworld).

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
│       ├── entrypoint.sh         # Starts Xvfb → fluxbox → challenge app → MCP server
│       ├── challenge.py          # Multi-step tkinter challenge GUI
│       └── server.py             # screenshot, click, type_text, press_key
├── tests/
│   ├── test.sh                   # Verifier entrypoint
│   └── test_outputs.py           # Pytest assertions
└── solution/
    └── solve.sh                  # Reference solution
```

## How it works

A companion container runs a virtual desktop (Xvfb + Fluxbox) alongside a FastMCP server that exposes `screenshot`, `click`, `type_text`, and `press_key` tools. The desktop and MCP server share a container because the tools need direct access to the X display.

A tkinter application (`challenge.py`) presents a multi-step challenge:
1. **Screen 1**: Welcome screen with a "Start Challenge" button
2. **Screen 2**: Passphrase prompt — the agent must type the displayed passphrase and click Submit
3. **Screen 3**: The secret code is revealed

The agent must take screenshots, interact with the GUI, and write the revealed secret code to a file.

The `[[environment.mcp_servers]]` section in `task.toml` declares the MCP server.

## Run

```bash
harbor run -p harbor_cookbook/recipes/computer-use --agent claude-code --model anthropic/claude-sonnet-4-6
```

## Limitations

Multi-container tasks require the **docker** environment provider because they rely on Docker Compose networking. They are not supported on cloud providers (Daytona, Modal, E2B, etc.).
