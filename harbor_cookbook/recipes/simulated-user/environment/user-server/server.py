"""Simulated user MCP server.

Uses an LLM with a persona file to generate realistic user responses
when the agent calls ask_user.
"""

import os
from pathlib import Path

import anthropic
from fastmcp import FastMCP

mcp = FastMCP("simulated-user")

client = anthropic.Anthropic()
MODEL = os.environ.get("SIM_USER_MODEL") or "claude-sonnet-4-6"

persona = Path("/app/persona.md").read_text()

SYSTEM_PROMPT = (
    "You are role-playing as a user talking to a coding assistant. "
    "Stay in character at all times. Never break character or mention that you are an AI.\n\n"
    f"{persona}"
)

conversation: list[dict] = []


@mcp.tool()
def ask_user(question: str) -> str:
    """Ask the user a question and get their response."""
    conversation.append({"role": "user", "content": question})

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        thinking={"type": "adaptive"},
        output_config={"effort": "low"},
        system=SYSTEM_PROMPT,
        messages=conversation,
    )

    # Store full content (including thinking blocks) in history for API compliance
    conversation.append({"role": "assistant", "content": response.content})

    # Return only text blocks to the agent
    text_parts = [block.text for block in response.content if block.type == "text"]
    return "\n".join(text_parts)


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
