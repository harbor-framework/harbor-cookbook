# computer-use-windows

Computer-use task on a remote Windows desktop. A companion MCP server creates a [Daytona](https://daytona.io) Windows sandbox, deploys a multi-step tkinter challenge, and proxies computer-use tools (screenshot, click, type) to the agent. Same tool set as `computer-use-ubuntu`, backed by the Daytona Computer Use API.

> **Note:** Daytona Windows Computer Use is currently in early preview. Access requires a beta account at [win.trydaytona.com](https://win.trydaytona.com/) with the `windows-base` snapshot available.

## Run

```bash
harbor run -p harbor_cookbook/recipes/computer-use-windows \
  --agent claude-code --model anthropic/claude-sonnet-4-6 \
  --env-file .env -y
```

Your `.env` needs:
```
DAYTONA_API_KEY=your_key_here
DAYTONA_API_URL=https://win.trydaytona.com/api
```

## Limitations

- Requires internet access (MCP server connects to the Daytona API)
- Windows sandbox takes ~30-60s to start after creation
