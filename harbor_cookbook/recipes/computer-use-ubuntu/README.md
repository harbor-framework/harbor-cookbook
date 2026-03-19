# computer-use-ubuntu

Computer-use task where an agent interacts with an Ubuntu (XFCE4) virtual desktop to solve a multi-step GUI challenge. The tool set mirrors the [Anthropic computer-use demo](https://github.com/anthropics/claude-quickstarts/tree/main/computer-use-demo). Desktop setup based on the [Harbor OSWorld adapter](https://github.com/Mascobot/harbor/tree/main/adapters/osworld).

## How it works

A companion container runs an Ubuntu desktop (Xvfb + XFCE4) alongside a FastMCP server that exposes computer-use tools. The desktop and MCP server share a container because the tools need direct access to the X display.

A tkinter application (`challenge.py`) presents a multi-step challenge that requires the agent to click buttons, type text, and read the result from the screen. The task cannot be solved without genuine GUI interaction.

## Run

```bash
harbor run -p harbor_cookbook/recipes/computer-use-ubuntu --agent claude-code --model anthropic/claude-sonnet-4-6
```

## Limitations

Multi-container tasks require the **docker** environment provider because they rely on Docker Compose networking. They are not supported on cloud providers (Daytona, Modal, E2B, etc.).
