"""Tests that the agent retrieved values from the MCP server."""

from pathlib import Path

SECRET_VALUE = "cookbook-mcp-secret-42"


def test_secret_file_exists():
    assert Path("/app/secret.txt").exists(), "secret.txt was not created"


def test_secret_file_contents():
    content = Path("/app/secret.txt").read_text().strip()
    assert content == SECRET_VALUE, (
        f"secret.txt contains '{content}', expected '{SECRET_VALUE}'"
    )


def test_timestamp_file_exists():
    assert Path("/app/timestamp.txt").exists(), "timestamp.txt was not created"


def test_timestamp_file_not_empty():
    content = Path("/app/timestamp.txt").read_text().strip()
    assert len(content) > 0, "timestamp.txt is empty"
