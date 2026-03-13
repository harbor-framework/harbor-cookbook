# Harbor Cookbook

[![Docs](https://img.shields.io/badge/Docs-000000?style=for-the-badge&logo=mdbook&color=105864)](https://harborframework.com/docs)

Realistic examples of building evals and optimizing agents using [Harbor](https://github.com/harbor-framework/harbor).

Each recipe in `harbor_cookbook/recipes` is self-contained and runnable. They show recurring patterns for Harbor tasks: single containers, multi-service setups, MCP tools, and simulated users.

## Getting Started

Install Harbor:

```bash
uv tool install harbor
```

Run any recipe:

```bash
harbor run -p recipes/<name>/task -a claude-code -m anthropic/claude-opus-4-6
```

## Recipes

| Name | Description |
|--------|-------------|
| [simple-task](recipes/simple-task/) | Bare-minimum task: one Dockerfile, an instruction, a pytest test, and a reference solution. |
| [multi-container](recipes/multi-container/) |Adding a companion service (a REST API) via Docker Compose that the agent interacts with over the network. |
| [mcp-tools](recipes/mcp-tools/) | Agent gets custom tools via an MCP server (declared in `task.toml`, served over streamable-http). The agent discovers and calls tools through its native MCP support. |
| [simulated-user](recipes/simulated-user/) | The agent can ask questions to a simulated user via a tool call. |

See each recipe's README for structure and details.
