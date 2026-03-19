# sidecar-dns

DNS filtering via a dnsmasq sidecar container. The `main` container uses the sidecar as its DNS server; blocked domains return NXDOMAIN.

## How it works

Two containers on a custom Docker network (`dnsnet`, `10.0.0.0/24`):

1. **`main`** (agent) — `dns: 10.0.0.53` routes all DNS queries through the sidecar
2. **`dns-server`** — dnsmasq at `10.0.0.53`; blocks `google.com` and `wikipedia.org`, forwards everything else to `8.8.8.8`

## Run

```bash
# Docker
harbor run -p harbor_cookbook/recipes/sidecar-dns --agent codex --model openai/o4-mini

# Daytona (requires a docker-dind snapshot)
harbor run -p harbor_cookbook/recipes/sidecar-dns --agent codex --model openai/o4-mini --env daytona --ek dind_snapshot=docker-dind
```
