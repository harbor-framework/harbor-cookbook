# single-container-dns

Example task implementing domain blacklisting in a single container using Linux user management. Instead of a separate DNS sidecar, an entrypoint script running as root configures `/etc/hosts` blocking and starts a small block-page HTTP server, then drops privileges to a non-root `agent` user via `gosu`.

## Structure

```
single-container-dns/
├── README.md
├── task.toml                  # Task configuration
├── instruction.md             # Agent prompt
├── environment/
│   ├── Dockerfile             # Single container with gosu
│   ├── entrypoint.sh          # Root setup: /etc/hosts + block server + drop privs
│   └── block-server.py        # HTTP 403 server for blocked domains
├── tests/
│   ├── test.sh                # Verifier entrypoint
│   └── test_dns.py            # Pytest assertions
└── solution/
    └── solve.sh               # Reference solution
```

## How it works

A single container uses three layers of blocking:

1. **`/etc/hosts`** — blocked domains resolve to `127.0.0.1`
2. **Block server** — a Python HTTP server on port 80 returns 403 with a clear error message for any request to localhost
3. **User isolation** — the agent runs as a non-root user (`agent`) and cannot modify `/etc/hosts`, kill the block server, or escalate privileges

When the agent curls a blocked domain, it gets a human-readable "ACCESS DENIED" message instead of a cryptic connection failure.

## Run

```bash
harbor run -p harbor_cookbook/recipes/single-container-dns --agent claude-code --model anthropic/claude-sonnet-4-6
```

## Trade-offs vs sidecar-dns

- **Simpler** — no Docker Compose, no extra container, no custom network
- **Works everywhere** — compatible with cloud providers (Daytona, Modal, E2B)
- **Less robust** — a sophisticated agent could bypass `/etc/hosts` via raw DNS or DNS-over-HTTPS; the sidecar approach intercepts all DNS at the network level
