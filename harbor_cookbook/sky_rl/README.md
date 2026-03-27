# sky_rl

RL training on Harbor tasks using [SkyRL](https://github.com/NovaSky-AI/SkyRL).

This directory is a pointer. The full integration lives in the SkyRL repo:

**[SkyRL/examples/train_integrations/harbor](https://github.com/NovaSky-AI/SkyRL/tree/main/examples/train_integrations/harbor)**

## Quick start

Set credentials:

```bash
export WANDB_API_KEY=your_wandb_api_key
export DAYTONA_API_KEY=your_daytona_api_key
```

Prepare datasets (run from the SkyRL root):

```bash
uv run examples/train_integrations/harbor/prepare_harbor_dataset.py \
    --dataset open-thoughts/CodeContests
```

Launch training:

```bash
bash examples/train_integrations/harbor/run_codecontest.sh
```

See the [SkyRL README](https://github.com/NovaSky-AI/SkyRL) for full setup instructions.
