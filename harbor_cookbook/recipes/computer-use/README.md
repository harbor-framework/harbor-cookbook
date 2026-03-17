# computer-use

Computer-use task where an agent interacts with a virtual desktop to solve a multi-step GUI challenge. The tool set mirrors the [Anthropic computer-use demo](https://github.com/anthropics/claude-quickstarts/tree/main/computer-use-demo).

## How it works

A companion container runs an Ubuntu desktop (Xvfb + XFCE4) alongside a FastMCP server that exposes computer-use tools. The desktop and MCP server share a container because the tools need direct access to the X display.

A tkinter application (`challenge.py`) presents a multi-step challenge that requires the agent to click buttons, type text, and read the result from the screen. The task cannot be solved without genuine GUI interaction.

## Run

```bash
harbor run -p harbor_cookbook/recipes/computer-use --agent claude-code --model anthropic/claude-sonnet-4-6
```

## Ubuntu and Windows support

This recipe runs an Ubuntu (XFCE4) desktop by default. The same pattern can be adapted for Windows using QEMU-based containers (e.g. [`dockurr/windows`](https://github.com/dockur/windows)) — the MCP server would use VNC for screenshots and input instead of X11 tools. For a production-grade implementation of both Ubuntu and Windows desktop environments, see the [Harbor OSWorld adapter](https://github.com/Mascobot/harbor/tree/main/adapters/osworld), which this recipe's desktop setup is based on.

## Limitations

Multi-container tasks require the **docker** environment provider because they rely on Docker Compose networking. They are not supported on cloud providers (Daytona, Modal, E2B, etc.).
