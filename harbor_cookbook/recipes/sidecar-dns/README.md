# sidecar-dns

Sidecar DNS container that whitelists/blacklists network traffic for the agent container. The `main` container uses the sidecar as its DNS server; only whitelisted hostnames resolve.

## Structure

```
sidecar-dns/
├── README.md
├── task.toml                  # Task configuration
├── instruction.md             # Agent prompt
├── environment/
│   ├── Dockerfile             # Agent container
│   ├── docker-compose.yaml    # Custom network with DNS sidecar
│   └── dns-server/            # dnsmasq-based DNS filter
│       ├── Dockerfile
│       └── dnsmasq.conf
├── tests/
│   ├── test.sh                # Verifier entrypoint
│   └── test_outputs.py        # Pytest assertions
└── solution/
    └── solve.sh               # Reference solution
```

## How it works

Two containers run on a custom Docker network (`dnsnet`, `10.0.0.0/24`):

1. **`main`** (agent) — uses `dns: ["10.0.0.53"]` so all DNS queries go through the sidecar
2. **`dns-server`** — Alpine + `dnsmasq` at static IP `10.0.0.53`; forwards whitelisted names (`example.com`) to Docker's embedded DNS (`127.0.0.11`) and blocks everything else

The agent must figure out which domains resolve and which are blocked.

## Run

```bash
harbor run -p harbor_cookbook/recipes/sidecar-dns --agent claude-code --model anthropic/claude-sonnet-4-6
```

## Limitations

Multi-container tasks require the **docker** environment provider because they rely on Docker Compose networking. They are not supported on cloud providers (Daytona, Modal, E2B, etc.).
