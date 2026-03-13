# /// script
# requires-python = ">=3.12"
# dependencies = ["fastmcp"]
# ///
"""MCP server exposing tools for the agent to call."""

from datetime import datetime, timezone

from fastmcp import FastMCP

mcp = FastMCP("mcp-tools")

SECRET_VALUE = "cookbook-mcp-secret-42"
STARTUP_TIME = datetime.now(timezone.utc).isoformat()


@mcp.tool()
def get_secret() -> str:
    """Returns a secret value."""
    return SECRET_VALUE


@mcp.tool()
def get_timestamp() -> str:
    """Returns the server's startup timestamp in ISO 8601 format."""
    return STARTUP_TIME


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
