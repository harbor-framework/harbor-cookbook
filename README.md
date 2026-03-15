# Harbor Cookbook

[![Docs](https://img.shields.io/badge/Docs-000000?style=for-the-badge&logo=mdbook&color=105864)](https://harborframework.com/docs)

Realistic examples of building evals and optimizing agents using [Harbor](https://github.com/harbor-framework/harbor). 

## Getting Started

Install Harbor:

```bash
uv tool install harbor
```

Run any task recipe:

```bash
harbor run -p harbor_cookbook/recipes/<name> -a claude-code -m anthropic/claude-opus-4-6
```

## Task Recipes

| Name                                                        | Description |
|-------------------------------------------------------------|-------------|
| [simple-task](harbor_cookbook/recipes/simple-task/)           | Bare-minimum task: one Dockerfile, an instruction, a pytest test, and a reference solution. |
| [multi-container](harbor_cookbook/recipes/multi-container/)   | Adding a companion service (a REST API) via Docker Compose that the agent interacts with over the network. |
| [mcp-tools](harbor_cookbook/recipes/mcp-tools/)               | Agent gets custom tools via an MCP server (declared in `task.toml`, served over streamable-http). The agent discovers and calls tools through its native MCP support. |
| [simulated-user](harbor_cookbook/recipes/simulated-user/)     | The agent can ask questions to a simulated user via a tool call. |
| [computer-use](harbor_cookbook/recipes/computer-use/)         | Computer-use task with a virtual desktop and MCP tools for screenshots, clicks, typing, etc. |
| [sidecar-dns](harbor_cookbook/recipes/sidecar-dns/)           | Sidecar DNS container that whitelists/blacklists network traffic for the agent. |

See each recipe's README for structure and details.
