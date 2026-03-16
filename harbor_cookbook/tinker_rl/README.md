# tinker_rl

RL training on Harbor tasks using the [Tinker SDK](https://github.com/thinking-machines-lab/tinker-cookbook).

This directory is a pointer. the full recipe example lives in the tinker-cookbook repo:

**[tinker-cookbook/harbor_rl](https://github.com/thinking-machines-lab/tinker-cookbook/tree/main/tinker_cookbook/recipes/harbor_rl)**

## Quick start

Download Harbor tasks (e.g. Terminal-Bench 2.0):

```bash
harbor datasets download terminal-bench@2.0
```

Launch training:

```bash
python -m tinker_cookbook.recipes.harbor_rl.launch_terminal_bench \
    model_name="moonshotai/Kimi-K2-Thinking" \
    group_size=4 \
    groups_per_batch=8 \
    learning_rate=1e-5 \
    lora_rank=32 \
    max_tokens=8192
```

See the [tinker-cookbook README](https://github.com/thinking-machines-lab/tinker-cookbook) for setup instructions.
