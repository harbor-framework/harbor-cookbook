# Harbor Cookbook Agent Guide

## Overview

This repo contains recipes — self-contained examples showing how to build evaluations with [Harbor](https://github.com/laude-institute/harbor).

Each recipe lives under `harbor_cookbook/recipes/<name>/` and contains a `README.md` plus a `task/` directory that Harbor can run directly.

## Repo Structure

```
harbor-cookbook/
├── README.md
├── CLAUDE.md              # Agent guide (identical to AGENTS.md)
├── AGENTS.md              # Agent guide (identical to CLAUDE.md)
├── LICENSE
├── pyproject.toml
├── .github/workflows/
│   └── ci.yml
└── harbor_cookbook/
    └── recipes/
        ├── registry.json      # Recipe index (mirrors Harbor's dataset registry format)
        ├── simple-task/
        ├── multi-container/
        ├── mcp-tools/
        └── simulated-user/
```

## Registry

`harbor_cookbook/recipes/registry.json` is the recipe index. Each entry has a `name`, `description`, and `path`. CI validates that every recipe directory has a registry entry and every entry's path exists.

## Recipe Structure

Every recipe has:

```
harbor_cookbook/recipes/<name>/
├── README.md              # What this recipe demonstrates and how to run it
└── task/
    ├── task.toml          # Task configuration (timeouts, resources, MCP servers)
    ├── instruction.md     # Natural language instruction for the agent
    ├── environment/
    │   ├── Dockerfile     # Agent container
    │   └── ...            # Optional: docker-compose.yaml, service dirs
    ├── tests/
    │   ├── test.sh        # Entrypoint — installs deps, runs tests, writes reward
    │   └── test_*.py      # Pytest test files
    └── solution/
        └── solve.sh       # Reference solution
```

## Task Conventions

- `test.sh` writes `1` or `0` to `/logs/verifier/reward.txt`
- Tests use pytest with CTRF output: `pytest --ctrf /logs/verifier/ctrf.json`
- Install test deps inside `test.sh` (the verifier container is clean)
- Dockerfiles use `ubuntu:24.04` unless there's a reason not to

## Running a Recipe

```bash
harbor run -p harbor_cookbook/recipes/<name>/task --agent claude-code --model anthropic/claude-sonnet-4-1
```

## Code Style

```bash
uv run ruff check .
uv run ruff format .
```
