# Harbor Cookbook

 [![](https://dcbadge.limes.pink/api/server/https://discord.gg/6xWPKhGDbA)](https://discord.gg/6xWPKhGDbA)
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
| [simple&#8209;task](harbor_cookbook/recipes/simple-task/) | Minimal single-container task. |
| [multi&#8209;container](harbor_cookbook/recipes/multi-container/) | Docker Compose task where the agent interacts with a locally hosted REST API. |
| [postgres&#8209;snapshot&#8209;regrade](harbor_cookbook/recipes/postgres-snapshot-regrade/) | Capture PostgreSQL state, grade it in a separate verifier, and regrade the saved snapshot. |
| [mcp&#8209;tools](harbor_cookbook/recipes/mcp-tools/) | Giving the agent custom tools via a locally hosted FastMCP server. |
| [multi&#8209;reward](harbor_cookbook/recipes/multi-reward/) | Multiple independent verifiers each producing their own score. |
| [simulated&#8209;user](harbor_cookbook/recipes/simulated-user/) | Agent discovers requirements by talking to a simulated user. |
| [computer&#8209;use&#8209;ubuntu](harbor_cookbook/recipes/computer-use-ubuntu/) | Computer use reference implementation on an Ubuntu virtual desktop. |
| [computer&#8209;use&#8209;windows](harbor_cookbook/recipes/computer-use-windows/) | Computer use reference implementation on a remote Windows desktop (Daytona). |
| [dns&#8209;blacklisting](harbor_cookbook/recipes/dns-blacklisting/) | Network-level hostname blacklisting with exact, wildcard, and regex rules. |
| [skills](harbor_cookbook/recipes/skills/) | Giving agents access to custom skills. |
| [multi&#8209;step](harbor_cookbook/recipes/multi-step/) | Ordered multi-step task with per-step instructions, tests, workdir uploads, healthcheck, early stopping, and per-step artifacts. |

## Optimization Examples

| Name | Description |
|:--|:--|
| [cortex&#8209;rl](harbor_cookbook/cortex_rl/) | RL post-training on Harbor tasks using Snowflake Cortex Training. |
| [harbor&#8209;rl](harbor_cookbook/harbor_rl/) | RL training on Harbor tasks using harbor.rl + Tinker. |
| [gepa](harbor_cookbook/gepa/) | Agent harness optimization for MedAgentBench using Harbor+GEPA. |
| [tinker&#8209;rl](harbor_cookbook/tinker_rl/) | RL training on Harbor tasks using the Tinker Cookbook integration. |
| [prime&#8209;rl](harbor_cookbook/prime_rl/) | RL training on Harbor tasks using Prime RL and Verifiers. |
| [sky&#8209;rl](harbor_cookbook/sky_rl/) | RL training on Harbor tasks using SkyRL. |
