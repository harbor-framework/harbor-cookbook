"""Tests that the agent correctly identified which domains resolve."""

from pathlib import Path


def test_resolved_file_exists():
    assert Path("/app/resolved.txt").exists(), "resolved.txt was not created"


def test_only_whitelisted_domains():
    content = Path("/app/resolved.txt").read_text().strip()
    domains = content.splitlines()
    assert domains == ["example.com"], f"Expected only ['example.com'], got {domains}"
