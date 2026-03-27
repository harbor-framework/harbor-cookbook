# /// script
# requires-python = ">=3.12"
# dependencies = ["fastmcp", "daytona==0.131.0a1"]
# ///
"""MCP server exposing computer-use tools backed by a Daytona Windows sandbox.

On startup the server creates a Windows sandbox from the ``windows-base``
snapshot, deploys a tkinter challenge application, and launches it on the
desktop.  Every MCP tool call is proxied to the sandbox via the Daytona
Computer Use API.

If the sandbox cannot be created (e.g. missing credentials), the server
still starts so that Docker healthchecks pass and oracle tests work.
"""

import atexit
import base64
import functools
import logging
import os
import time

from fastmcp import FastMCP
from fastmcp.utilities.types import Image

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

WIN_APP_DIR = "C:/Users/Administrator/harbor"

sandbox = None


def _setup_sandbox():
    """Create the Windows sandbox and deploy the challenge app."""
    global sandbox

    from daytona import CreateSandboxFromSnapshotParams, Daytona, DaytonaConfig

    api_url = os.environ.get("DAYTONA_API_URL", "https://win.trydaytona.com/api")
    log.info("Connecting to Daytona at %s", api_url)
    daytona = Daytona(
        DaytonaConfig(
            api_key=os.environ["DAYTONA_API_KEY"],
            api_url=api_url,
        )
    )

    log.info("Creating Windows sandbox from 'windows-base' snapshot …")
    sandbox = daytona.create(
        CreateSandboxFromSnapshotParams(snapshot="windows-base"),
        timeout=120,
    )
    log.info("Sandbox created: %s (state=%s)", sandbox.id, sandbox.state)

    def _cleanup():
        try:
            log.info("Deleting sandbox %s …", sandbox.id)
            daytona.delete(sandbox)
        except Exception as exc:
            log.warning("Sandbox cleanup failed: %s", exc)

    atexit.register(_cleanup)

    try:
        sandbox.computer_use.start()
        log.info("computer_use.start() succeeded")
    except Exception as exc:
        log.info("computer_use.start() skipped: %s", exc)

    sandbox.process.exec(f"mkdir {WIN_APP_DIR}", timeout=5)

    log.info("Deploying challenge app …")
    with open(os.path.join(os.path.dirname(__file__) or ".", "challenge.py")) as f:
        challenge_source = f.read()

    sandbox.fs.upload_file(challenge_source.encode(), f"{WIN_APP_DIR}/challenge.py")

    # DETACHED_PROCESS flag so the GUI outlives the launcher
    launcher = (
        "import subprocess\n"
        "subprocess.Popen(\n"
        f"    ['python', r'{WIN_APP_DIR}/challenge.py'],\n"
        "    creationflags=0x00000008,\n"
        ")\n"
        "print('launched')\n"
    )
    sandbox.fs.upload_file(launcher.encode(), f"{WIN_APP_DIR}/launch.py")

    log.info("Launching challenge app on desktop …")
    r = sandbox.process.exec(f"python {WIN_APP_DIR}/launch.py", timeout=15)
    log.info("Launch result: %s", r.result)
    time.sleep(5)

    try:
        windows = sandbox.computer_use.display.get_windows()
        titles = [w.title for w in windows.windows] if windows.windows else []
        log.info("Open windows: %s", titles)
        if not any("Harbor" in t for t in titles):
            log.warning("Challenge window not found, retrying …")
            sandbox.process.exec(f"python {WIN_APP_DIR}/launch.py", timeout=15)
            time.sleep(5)
    except Exception as exc:
        log.warning("Could not verify window list: %s", exc)

    log.info("Setup complete")


try:
    _setup_sandbox()
except Exception as exc:
    log.warning("Sandbox setup failed (tools will be unavailable): %s", exc)

log.info("Starting MCP server (sandbox=%s)", "ready" if sandbox else "unavailable")

mcp = FastMCP("computer-use")


def requires_sandbox(fn):
    """Decorator that raises if the Windows sandbox is unavailable."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        if sandbox is None:
            raise RuntimeError(
                "Windows sandbox is not available. "
                "Check DAYTONA_API_KEY and DAYTONA_API_URL."
            )
        return fn(*args, **kwargs)

    return wrapper


@mcp.tool()
@requires_sandbox
def screenshot() -> Image:
    """Take a screenshot of the Windows desktop and return it as an image."""
    resp = sandbox.computer_use.screenshot.take_full_screen()
    return Image(data=base64.b64decode(resp.screenshot), format="png")


@mcp.tool()
@requires_sandbox
def mouse_move(x: int, y: int) -> str:
    """Move the mouse cursor to the given (x, y) pixel coordinate."""
    result = sandbox.computer_use.mouse.move(x, y)
    return f"Moved mouse to ({result.x}, {result.y})"


@mcp.tool()
@requires_sandbox
def left_click(x: int, y: int) -> str:
    """Left-click at the given (x, y) pixel coordinate."""
    sandbox.computer_use.mouse.click(x, y)
    return f"Left clicked at ({x}, {y})"


@mcp.tool()
@requires_sandbox
def right_click(x: int, y: int) -> str:
    """Right-click at the given (x, y) pixel coordinate."""
    sandbox.computer_use.mouse.click(x, y, button="right")
    return f"Right clicked at ({x}, {y})"


@mcp.tool()
@requires_sandbox
def middle_click(x: int, y: int) -> str:
    """Middle-click at the given (x, y) pixel coordinate."""
    sandbox.computer_use.mouse.click(x, y, button="middle")
    return f"Middle clicked at ({x}, {y})"


@mcp.tool()
@requires_sandbox
def double_click(x: int, y: int) -> str:
    """Double-click at the given (x, y) pixel coordinate."""
    sandbox.computer_use.mouse.click(x, y, double=True)
    return f"Double clicked at ({x}, {y})"


@mcp.tool()
@requires_sandbox
def triple_click(x: int, y: int) -> str:
    """Triple-click at the given (x, y) coordinate (e.g. to select a line)."""
    sandbox.computer_use.mouse.click(x, y)
    sandbox.computer_use.mouse.click(x, y)
    sandbox.computer_use.mouse.click(x, y)
    return f"Triple clicked at ({x}, {y})"


@mcp.tool()
@requires_sandbox
def left_click_drag(start_x: int, start_y: int, end_x: int, end_y: int) -> str:
    """Click and drag from (start_x, start_y) to (end_x, end_y)."""
    sandbox.computer_use.mouse.drag(start_x, start_y, end_x, end_y)
    return f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})"


@mcp.tool()
@requires_sandbox
def scroll(x: int, y: int, direction: str, clicks: int = 3) -> str:
    """Scroll at (x, y). direction is 'up' or 'down'. clicks controls amount."""
    sandbox.computer_use.mouse.scroll(x, y, direction, clicks)
    return f"Scrolled {direction} {clicks} clicks at ({x}, {y})"


@mcp.tool()
@requires_sandbox
def cursor_position() -> str:
    """Return the current (x, y) position of the mouse cursor."""
    pos = sandbox.computer_use.mouse.get_position()
    return f"Cursor position: ({pos.x}, {pos.y})"


@mcp.tool()
@requires_sandbox
def type_text(text: str) -> str:
    """Type the given text on the Windows desktop."""
    sandbox.computer_use.keyboard.type(text)
    return f"Typed: {text}"


@mcp.tool()
@requires_sandbox
def press_key(key: str) -> str:
    """Press a key or key combination (e.g. 'Return', 'ctrl+c', 'alt+F4')."""
    if "+" in key:
        sandbox.computer_use.keyboard.hotkey(key)
    else:
        sandbox.computer_use.keyboard.press(key)
    return f"Pressed: {key}"


# hold_key is disabled: the Daytona keyboard API only has press() (full
# press+release) with no separate keydown/keyup, so the key is never truly
# held down.  Re-enable if Daytona adds keydown/keyup support.
#
# @mcp.tool()
# @requires_sandbox
# def hold_key(key: str, duration: float = 0.5) -> str:
#     """Hold a key down for the given duration in seconds."""
#     sandbox.computer_use.keyboard.press(key)
#     time.sleep(duration)
#     return f"Held {key} for {duration}s"


@mcp.tool()
def wait(seconds: float = 1.0) -> str:
    """Wait for the specified number of seconds."""
    time.sleep(seconds)
    return f"Waited {seconds} seconds"


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
