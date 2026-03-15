# /// script
# requires-python = ">=3.12"
# dependencies = ["fastmcp"]
# ///
"""MCP server exposing computer-use tools for interacting with a virtual desktop."""

import subprocess

from fastmcp import FastMCP
from fastmcp.utilities.types import Image

mcp = FastMCP("computer-use")

SCREENSHOT_PATH = "/tmp/screenshot.png"


@mcp.tool()
def screenshot() -> Image:
    """Take a screenshot of the virtual desktop and return it as an image."""
    subprocess.run(
        ["scrot", "--overwrite", SCREENSHOT_PATH],
        check=True,
        capture_output=True,
    )
    return Image(path=SCREENSHOT_PATH)


@mcp.tool()
def click(x: int, y: int) -> str:
    """Click at the given (x, y) pixel coordinate on the virtual desktop."""
    subprocess.run(
        ["xdotool", "mousemove", str(x), str(y), "click", "1"],
        check=True,
        capture_output=True,
    )
    return f"Clicked at ({x}, {y})"


@mcp.tool()
def type_text(text: str) -> str:
    """Type the given text on the virtual desktop."""
    subprocess.run(
        ["xdotool", "type", "--delay", "50", text],
        check=True,
        capture_output=True,
    )
    return f"Typed: {text}"


@mcp.tool()
def press_key(key: str) -> str:
    """Press a key or key combination (e.g. 'Return', 'ctrl+c', 'alt+F4')."""
    subprocess.run(
        ["xdotool", "key", key],
        check=True,
        capture_output=True,
    )
    return f"Pressed: {key}"


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
