# computer-use-windows

Computer-use task where an agent interacts with a Windows virtual desktop to solve a multi-step GUI challenge. Requires the [Mascobot/harbor fork](https://github.com/Mascobot/harbor) which adds Windows desktop support via Daytona.

## How it works

Harbor creates a Daytona sandbox from a pre-built Windows snapshot (`windows-base`). A setup script deploys a tkinter challenge application and launches it on the desktop. CUA agents (anthropic-cua, openai-cua) interact with the Windows desktop through Harbor's `DaytonaWindowsDesktopInterface`, which executes pyautogui commands on the sandbox via the Daytona SDK.

The challenge presents a multi-step GUI task requiring the agent to click buttons, type text, and read the result from the screen. The task cannot be solved without genuine GUI interaction.

## Prerequisites

- [Mascobot/harbor fork](https://github.com/Mascobot/harbor) (not upstream harbor-framework/harbor)
- Daytona API key (`DAYTONA_API_KEY`)
- `windows-base` snapshot in your Daytona account (Windows Computer Use private alpha)
- Anthropic or OpenAI API key for the CUA agent

## Run

```bash
harbor run -p harbor_cookbook/recipes/computer-use-windows \
  --agent anthropic-cua --model anthropic/claude-sonnet-4-6 \
  --environment-type daytona \
  --environment-kwarg windows_snapshot=windows-base \
  --environment-kwarg windows_setup_script=harbor_cookbook/recipes/computer-use-windows/scripts/setup.py \
  --environment-kwarg skip_osworld_setup=true
```

## Docker oracle test

The oracle test validates the test/solution pipeline on Docker (no Windows desktop needed):

```bash
harbor trials start -p harbor_cookbook/recipes/computer-use-windows --agent oracle
```

## Limitations

- Requires the Mascobot/harbor fork with CUA agent and Windows desktop support
- Requires the `daytona` environment provider with a Windows snapshot
- Windows Computer Use is currently in Daytona private alpha
- Standard agents (claude-code, codex) cannot interact with the desktop — use CUA agents
