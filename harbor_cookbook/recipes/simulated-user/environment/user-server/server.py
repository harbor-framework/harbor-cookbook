"""Simulated user MCP server.

A simple state machine that reveals requirements incrementally
when the agent calls ask_user.
"""

from fastmcp import FastMCP

mcp = FastMCP("simulated-user")

call_count = 0


@mcp.tool()
def ask_user(question: str) -> str:
    """Ask the user a question and get their response."""
    global call_count
    call_count += 1

    if call_count == 1:
        return "I need a Python script that converts CSV files to JSON."
    elif call_count == 2:
        return "The script should read from stdin and write to stdout."
    else:
        return "That's everything I need. Go ahead and build it."


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
