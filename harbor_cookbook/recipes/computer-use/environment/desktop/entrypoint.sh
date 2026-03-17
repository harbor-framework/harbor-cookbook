#!/bin/bash
set -e

# Start virtual framebuffer
Xvfb :99 -screen 0 1024x768x24 &
sleep 1

# Start window manager
fluxbox &
sleep 1

# Launch the challenge GUI
python3 challenge.py &
sleep 2

# Start the MCP server (foreground)
exec uv run server.py
