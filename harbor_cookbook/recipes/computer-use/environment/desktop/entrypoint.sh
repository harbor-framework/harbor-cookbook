#!/bin/bash
set -e

# Start virtual framebuffer
Xvfb :99 -screen 0 1280x1024x24 &
sleep 1

# Start XFCE4 desktop session
dbus-launch xfce4-session &
sleep 3

# Launch the challenge GUI
python3 challenge.py &
sleep 2

# Start the MCP server (foreground)
exec uv run server.py
