#!/bin/bash
set -e

# Start virtual framebuffer
Xvfb :99 -screen 0 1024x768x24 &
sleep 1

# Start window manager
fluxbox &
sleep 1

# Open a terminal displaying the secret code
xterm -hold -e "echo 'SECRET_CODE: HARBOR-CU-2025'" &
sleep 2

# Start the MCP server (foreground)
exec uv run server.py
