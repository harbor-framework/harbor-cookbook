# dns-filtering

Domain blacklisting via `/etc/hosts` and a block-page HTTP server. The agent runs as a non-root user and must figure out which domains are reachable.

## Structure

```
dns-filtering/
├── task.toml
├── instruction.md
├── environment/
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── block-server.py
├── tests/
│   ├── test.sh
│   └── test_dns.py
└── solution/
    └── solve.sh
```

## Run

```bash
harbor run -p harbor_cookbook/recipes/dns-filtering --agent claude-code --model anthropic/claude-sonnet-4-6
```


## How it works

The entrypoint runs as root and adds blocked domains to `/etc/hosts`, pointing them to `127.0.0.1`. A small Python HTTP server on port 80 returns a 403 "ACCESS DENIED" for any request to a blocked domain. The agent runs as a non-root user via `gosu` and cannot modify `/etc/hosts` or kill the block server.

## Limitations

This approach is not airtight. A sophisticated agent could bypass `/etc/hosts` by using raw DNS queries or DNS-over-HTTPS to resolve blocked domains directly.

