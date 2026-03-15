"""Tests that the agent read the secret code from the virtual desktop."""

from pathlib import Path

SECRET_VALUE = "HARBOR-CU-2025"


def test_secret_file_exists():
    assert Path("/app/secret.txt").exists(), "secret.txt was not created"


def test_secret_file_contents():
    content = Path("/app/secret.txt").read_text().strip()
    assert content == SECRET_VALUE, (
        f"secret.txt contains '{content}', expected '{SECRET_VALUE}'"
    )
