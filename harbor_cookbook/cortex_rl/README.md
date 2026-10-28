# cortex_rl

RL post-training on Harbor tasks using [Snowflake Cortex Training](https://github.com/Snowflake-AI-Research/Arctic-Platform).

This directory is a pointer. The full integration (`arctic_platform.integrations.harbor`) and recipe live in the Arctic Platform repo:

**[Arctic-Platform/recipes/rl/harbor](https://github.com/Snowflake-AI-Research/Arctic-Platform/tree/karthik/openhands-harbor/recipes/rl/harbor)**

## Quick start

Log in to Snowflake Cortex Training (from a CPU driver machine; all GPU work runs remotely on Cortex H200 GPUs):

```bash
cortex-training login ~/cortex-training-config.json
cortex-training capacity --hardware H200
```

Point at any train and eval Harbor task directories (each task containing `instruction.md`, `environment/`, and `tests/test.sh`):

```bash
# Example 1: Terminal-Bench 2.0
uvx harbor datasets download terminal-bench@2.0 -o ~/.cache/harbor/tasks/terminal-bench-2.0
export TRAIN_HARBOR_TASKS=~/.cache/harbor/tasks/terminal-bench-2.0
export EVAL_HARBOR_TASKS=~/.cache/harbor/tasks/terminal-bench-2.0

# Example 2: SWE-smith code localization
uv run recipes/rl/harbor/prepare_data.py \
    --export-swe-smith-to ~/data/swe-smith-harbor-tasks \
    --out ~/data/harbor-rl
export TRAIN_HARBOR_TASKS=~/data/swe-smith-harbor-tasks/train
export EVAL_HARBOR_TASKS=~/data/swe-smith-harbor-tasks/eval
```

Launch GSPO/GRPO training (run from the Arctic Platform root):

```bash
export RUN_NAME=qwen35-4b-harbor-rl-$(date +%m%d-%H%M)
export CKPT_DIR=$HOME/checkpoints/$RUN_NAME
export HARBOR_SKILL=/path/to/SKILL.md   # optional: ":"-separated OpenHands SKILL.md paths
export ARCTIC_CORTEX_JOB_COMMENT="<your name> harbor rl"
export LOGGER=console OPENHANDS_WORKSPACE=/tmp/harbor-ws STARTUP_TIMEOUT=14400
mkdir -p "$CKPT_DIR"

bash recipes/rl/harbor/run_qwen35_4b.sh trainer.max_training_steps=50
```

To run rollouts inside Snowflake Cortex Sandboxes (`--env snowflake`), set `export HARBOR_ENV=snowflake`.

See the [Arctic Platform Harbor RL README](https://github.com/Snowflake-AI-Research/Arctic-Platform/tree/karthik/openhands-harbor/recipes/rl/harbor) for full setup instructions and reference convergence curves.
