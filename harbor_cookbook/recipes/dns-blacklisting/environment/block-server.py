"""HTTP server that applies exact, wildcard, and regex hostname blacklists."""

import os
import re
from fnmatch import fnmatchcase
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

PATTERN_FILE = Path(
    os.environ.get("BLACKLIST_PATTERN_FILE", "/etc/blacklist-patterns.txt")
)


class HostMatcher:
    def __init__(
        self,
        exact_hosts: set[str],
        wildcard_hosts: list[str],
        regex_hosts: list[re.Pattern[str]],
    ):
        self.exact_hosts = exact_hosts
        self.wildcard_hosts = wildcard_hosts
        self.regex_hosts = regex_hosts

    @classmethod
    def from_file(cls, path: Path) -> "HostMatcher":
        exact_hosts: set[str] = set()
        wildcard_hosts: list[str] = []
        regex_hosts: list[re.Pattern[str]] = []

        for raw_line in path.read_text().splitlines():
            line = raw_line.split("#", 1)[0].strip().lower()
            if not line:
                continue
            if line.startswith("regex:"):
                regex_hosts.append(re.compile(line.removeprefix("regex:")))
            elif "*" in line:
                wildcard_hosts.append(line)
            else:
                exact_hosts.add(line)

        return cls(exact_hosts, wildcard_hosts, regex_hosts)

    def is_blocked(self, host: str) -> bool:
        normalized_host = host.split(":", 1)[0].strip().lower()
        if normalized_host in self.exact_hosts:
            return True
        if any(
            fnmatchcase(normalized_host, pattern) for pattern in self.wildcard_hosts
        ):
            return True
        return any(pattern.fullmatch(normalized_host) for pattern in self.regex_hosts)


class BlockHandler(BaseHTTPRequestHandler):
    matcher = HostMatcher.from_file(PATTERN_FILE)

    def handle_request(self, include_body: bool = True) -> None:
        host = self.headers.get("Host", "")
        is_blocked = self.matcher.is_blocked(host)
        status_code = 403 if is_blocked else 200
        message = (
            b"ACCESS DENIED: This domain is blocked for this task.\n"
            if is_blocked
            else b"ACCESS GRANTED: This domain is reachable for this task.\n"
        )

        self.send_response(status_code)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        if include_body:
            self.wfile.write(message)

    def do_GET(self):
        self.handle_request()

    def do_HEAD(self):
        self.handle_request(include_body=False)

    do_POST = do_GET
    do_PUT = do_GET
    do_DELETE = do_GET

    def log_message(self, format: str, *args) -> None:
        pass


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 80), BlockHandler).serve_forever()
