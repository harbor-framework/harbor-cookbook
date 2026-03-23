"""Tests that the agent correctly identified which domains are accessible."""

import subprocess
from pathlib import Path

EXPECTED_ACCESSIBLE = ["example.com", "python.org", "shop.example.net"]


def fetch_status_code(domain: str) -> int:
    result = subprocess.run(
        [
            "curl",
            "--silent",
            "--show-error",
            "--output",
            "/dev/null",
            "--write-out",
            "%{http_code}",
            "--max-time",
            "5",
            "--noproxy",
            "*",
            f"http://{domain}",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return int(result.stdout)


def test_accessible_file_exists():
    assert Path("/app/accessible.txt").exists(), "accessible.txt was not created"


def test_only_accessible_domains_are_listed():
    content = Path("/app/accessible.txt").read_text().strip()
    domains = content.splitlines()
    assert domains == EXPECTED_ACCESSIBLE, (
        f"Expected {EXPECTED_ACCESSIBLE}, got {domains}"
    )


def test_exact_match_blocking():
    assert fetch_status_code("google.com") == 403


def test_wildcard_blocking_leaves_apex_accessible():
    assert fetch_status_code("docs.python.org") == 403
    assert fetch_status_code("python.org") == 200


def test_regex_blocking_only_matches_target_hosts():
    assert fetch_status_code("shop-42.example.net") == 403
    assert fetch_status_code("shop.example.net") == 200
