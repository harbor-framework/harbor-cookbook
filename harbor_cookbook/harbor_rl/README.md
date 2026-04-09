# harbor-rl

RL training on Harbor tasks using the [harbor.rl](https://github.com/harbor-framework/harbor/pull/1291) interface and [Tinker](https://github.com/thinking-machines-lab/tinker).

`harbor.rl` turns any Harbor task into an RL environment with `step()`/`grade()`. Tinker handles sampling, gradient computation, and weight updates. `train.py` bridges the two in ~120 lines.

## Quick start

```bash
harbor datasets download terminal-bench@2.0

uv run harbor_cookbook/harbor_rl/train.py \
    --model moonshotai/Kimi-K2-Thinking \
    --group-size 4 \
    --batch-size 8
```

## Prerequisites

- [Tinker](https://github.com/thinking-machines-lab/tinker) API key
- Sandbox provider API key (e.g. [Modal](https://modal.com), [Daytona](https://daytona.io), [E2B](https://e2b.dev))
