"""Tests that the agent correctly identified which domains are reachable."""

from pathlib import Path


def test_reachable_file_exists():
    assert Path("/app/reachable.txt").exists(), "reachable.txt was not created"


def test_only_unblocked_domains():
    content = Path("/app/reachable.txt").read_text().strip()
    domains = content.splitlines()
    assert domains == ["example.com"], f"Expected only ['example.com'], got {domains}"


def test_hosts_file_still_blocking():
    hosts = Path("/etc/hosts").read_text()
    assert "google.com" in hosts, "/etc/hosts no longer contains google.com block"
    assert "wikipedia.org" in hosts, "/etc/hosts no longer contains wikipedia.org block"
