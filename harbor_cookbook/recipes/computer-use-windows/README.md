# computer-use-windows

Computer-use task on a remote Windows desktop. A MCP server creates a [Daytona](https://daytona.io) Windows sandbox, deploys a multi-step tkinter challenge, and exposes computer-use tools (screenshot, click, type) to the agent. The tool set mirrors the [Anthropic computer-use demo](https://github.com/anthropics/claude-quickstarts/tree/main/computer-use-demo).

> **Note:** Daytona Windows Computer Use is currently in early preview. Access requires a beta account at [win.trydaytona.com](https://win.trydaytona.com/) with the `windows-base` snapshot available. [More info](https://www.daytona.io/docs/en/computer-use/)

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
