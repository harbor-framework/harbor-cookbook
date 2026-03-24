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
| [simple&#8209;task](harbor_cookbook/recipes/simple-task/) | Minimal single-container task with a pytest verifier. |
| [multi&#8209;container](harbor_cookbook/recipes/multi-container/) | Docker Compose setup where the agent interacts with a companion service over the network. |
| [mcp&#8209;tools](harbor_cookbook/recipes/mcp-tools/) | Giving the agent custom tools via a FastMCP server in a companion container. |
| [simulated&#8209;user](harbor_cookbook/recipes/simulated-user/) | Agent discovers requirements by talking to a simulated user exposed as an MCP tool. |
| [computer&#8209;use&#8209;ubuntu](harbor_cookbook/recipes/computer-use-ubuntu/) | GUI interaction on an Ubuntu (XFCE4) virtual desktop via screenshot/click/type MCP tools. |
| [computer&#8209;use&#8209;windows](harbor_cookbook/recipes/computer-use-windows/) | GUI interaction on a remote Windows desktop (Daytona) via MCP tools. |
| [dns&#8209;blacklisting](harbor_cookbook/recipes/dns-blacklisting/) | Network-level hostname blacklisting with exact, wildcard, and regex rules. |
| [multi&#8209;reward](harbor_cookbook/recipes/multi-reward/) | Multiple independent verifiers each producing their own score. |

## Optimization Examples

| Name | Description |
|:--|:--|
| [gepa](harbor_cookbook/gepa/) | Agent harness optimization for MedAgentBench using Harbor+GEPA. |
| [tinker&#8209;rl](harbor_cookbook/tinker_rl/) | RL training on Harbor tasks using the Tinker SDK. |
