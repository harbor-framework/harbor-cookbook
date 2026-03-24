# computer-use-windows

Computer-use task where an agent interacts with a Windows virtual desktop to solve a multi-step GUI challenge. The desktop runs in a remote [Daytona](https://daytona.io) Windows sandbox, and a companion MCP server proxies computer-use tools (screenshot, click, type) to the agent.

## How it works

A companion Docker container runs a FastMCP server that creates a Daytona Windows sandbox from the `windows-base` snapshot, deploys a tkinter challenge application, and exposes computer-use tools over MCP. The agent interacts with the Windows desktop through these tools — the same tool set as the `computer-use-ubuntu` recipe, but backed by the Daytona Computer Use API instead of local xdotool/scrot.

The challenge presents a multi-step GUI task requiring the agent to click buttons, type text, and read the result from the screen. The task cannot be solved without genuine GUI interaction.

## Prerequisites

- Daytona beta environment access at [win.trydaytona.com](https://win.trydaytona.com/)
- `DAYTONA_API_KEY` (org-level key from the beta dashboard)
- `DAYTONA_API_URL=https://win.trydaytona.com/api`
- `windows-base` snapshot available in your Daytona beta account

## Run

```bash
harbor run -p harbor_cookbook/recipes/computer-use-windows \
  --agent claude-code --model anthropic/claude-sonnet-4-6 \
  --env-file .env -y
```

Your `.env` should contain:
```
DAYTONA_API_KEY=your_key_here
DAYTONA_API_URL=https://win.trydaytona.com/api
```

## Limitations

- Requires internet access (the MCP server connects to the Daytona API)
- Requires a Daytona beta account with the `windows-base` snapshot
- The Windows sandbox takes ~30-60s to become responsive after creation
