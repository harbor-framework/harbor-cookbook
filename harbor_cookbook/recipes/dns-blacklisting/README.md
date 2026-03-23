# dns-blacklisting

Pattern-based hostname blacklisting via a local HTTP gateway. The agent must figure out which domains are reachable when exact, wildcard, and regex rules are in play.

## Structure

```
dns-blacklisting/
├── task.toml
├── instruction.md
├── environment/
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── blacklist-patterns.txt
│   ├── candidate-domains.txt
│   └── block-server.py
├── tests/
│   ├── test.sh
│   └── test_dns.py
└── solution/
    └── solve.sh
```

## Run

```bash
harbor run -p harbor_cookbook/recipes/dns-blacklisting --agent claude-code --model anthropic/claude-sonnet-4-6
```


## How it works

The entrypoint routes the task's candidate domains to `127.0.0.1` so every request hits a local Python HTTP server. That server inspects the request `Host` header and decides whether to return `200 OK` or `403 ACCESS DENIED` based on rules loaded from `blacklist-patterns.txt`.

Supported pattern formats:

- `google.com` for an exact hostname match
- `*.python.org` for wildcard subdomain matches
- `regex:^shop-[0-9]+\.example\.net$` for regular-expression matches

## Limitations

This is still a teaching recipe, not a hardened network control. An agent could inspect or modify the seeded files, or bypass the recipe's routing setup entirely. The verifier therefore checks the final runtime behavior of the candidate domains rather than trusting the seed files alone.
