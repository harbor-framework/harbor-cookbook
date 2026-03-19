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

| Name | Description |
|:--|:--|
| [simple&#8209;task](harbor_cookbook/recipes/simple-task/) | Bare-minimum task: one Dockerfile, an instruction, a pytest test, and a reference solution. |
| [multi&#8209;container](harbor_cookbook/recipes/multi-container/) | Adding a companion service (e.g. a REST API) that the agent interacts with over the network. |
| [mcp&#8209;tools](harbor_cookbook/recipes/mcp-tools/) | Agent gets custom tools via an MCP server. |
| [simulated&#8209;user](harbor_cookbook/recipes/simulated-user/) | The agent can ask questions to a simulated user via a tool call. |
| [computer&#8209;use](harbor_cookbook/recipes/computer-use/) | Computer-use task with a virtual desktop and MCP tools for screenshots, clicks, typing, etc. |
| [dns&#8209;blacklisting](harbor_cookbook/recipes/dns-blacklisting/) | Domain blacklisting via `/etc/hosts` and a block-page HTTP server with non-root user isolation. |
| [multi&#8209;reward](harbor_cookbook/recipes/multi-reward/) | Multiple verifiers that grade independently and write separate rewards to `reward.json`. |

## Optimization Examples

| Name | Description |
|:--|:--|
| [gepa](harbor_cookbook/gepa/) | Agent harness optimization for MedAgentBench using Harbor+GEPA. |
| [tinker&#8209;rl](harbor_cookbook/tinker_rl/) | RL training on Harbor tasks using the Tinker SDK. |
