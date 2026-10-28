# cortex_rl

Go from any [Harbor](https://github.com/harbor-framework/harbor) evaluation tasks to RL post-training on **Snowflake Cortex Training** in two environment variables (`TRAIN_HARBOR_TASKS` and `EVAL_HARBOR_TASKS`).

Every Harbor task already defines the three pieces an RL rollout needs:
1. `instruction.md`: the prompt shown to the agent.
2. `environment/`: the sandbox (`--env snowflake`, `docker`, `modal`, `daytona`, or `HostEnvironment`).
3. `tests/test.sh`: the verifier that writes `/logs/verifier/reward.txt` or `/logs/verifier/reward.json`.

Cortex Training's Harbor integration (`arctic_platform.integrations.harbor`) wires Harbor's `Trial` and `Verifier` directly into an online GSPO/GRPO loop — no custom rollout adapter, reward wrapper, or local GPUs required. Point at your Harbor task directories, optionally attach an OpenHands `SKILL.md`, and launch from a CPU driver machine while Cortex Training runs distributed vLLM sampling and FSDP/Megatron policy updates on remote H200 GPUs.

This directory is a pointer. The full integration and recipe live in the Arctic Platform repo:

**[Arctic-Platform/recipes/rl/harbor](https://github.com/Snowflake-AI-Research/Arctic-Platform/tree/karthik/openhands-harbor/recipes/rl/harbor)**

## From Harbor tasks to RL in 3 steps

### 1. Log in to Snowflake Cortex Training

Run from any CPU driver machine (all GPU sampling and training run remotely on Cortex H200 GPUs):

```bash
cortex-training login ~/cortex-training-config.json
cortex-training capacity --hardware H200
```

### 2. Point at your train and eval Harbor task directories

Use any directory of Harbor tasks (downloaded from Harbor Hub, converted from an existing benchmark, or authored with `harbor task init`):

```bash
# Any Harbor task directories
export TRAIN_HARBOR_TASKS=/path/to/train_harbor_tasks
export EVAL_HARBOR_TASKS=/path/to/eval_harbor_tasks

# Or download a Harbor dataset directly (e.g. Terminal-Bench 2.0)
uvx harbor datasets download terminal-bench@2.0 -o ~/.cache/harbor/tasks/terminal-bench-2.0
export TRAIN_HARBOR_TASKS=~/.cache/harbor/tasks/terminal-bench-2.0
export EVAL_HARBOR_TASKS=~/.cache/harbor/tasks/terminal-bench-2.0
```

### 3. Launch RL post-training

`recipes/rl/harbor/run_qwen35_4b.sh` automatically discovers every Harbor task under `TRAIN_HARBOR_TASKS` and `EVAL_HARBOR_TASKS`, builds the dataset parquets, spins up per-rollout OpenAI proxies + Harbor trials (`64` concurrent rollouts/step), grades each trial with Harbor's `Verifier`, and updates the model weights:

```bash
export RUN_NAME=qwen35-4b-harbor-rl-$(date +%m%d-%H%M)
export CKPT_DIR=$HOME/checkpoints/$RUN_NAME
export HARBOR_SKILL=/path/to/SKILL.md   # optional: ":"-separated OpenHands SKILL.md paths
export ARCTIC_CORTEX_JOB_COMMENT="<your name> harbor rl"
export LOGGER=console OPENHANDS_WORKSPACE=/tmp/harbor-ws STARTUP_TIMEOUT=14400
mkdir -p "$CKPT_DIR"

bash recipes/rl/harbor/run_qwen35_4b.sh trainer.max_training_steps=50
```

## Swap agents, skills, or sandboxes with one env var

| Variable | Default | What it controls |
| :--- | :--- | :--- |
| `TRAIN_HARBOR_TASKS` | — | Directory of training Harbor tasks (`instruction.md` + `environment/` + `tests/test.sh`) |
| `EVAL_HARBOR_TASKS` | `TRAIN_HARBOR_TASKS` | Directory of evaluation Harbor tasks |
| `HARBOR_SKILL` | — | Optional `:`-separated `SKILL.md` file(s) or skill directories loaded into the agent |
| `HARBOR_ENV` | `HostEnvironment` | Any Harbor `--env` provider (`snowflake`, `docker`, `modal`, `daytona`, `e2b`, etc.) |
| `HARBOR_AGENT` | `OpenHandsHarborAgent` | Any Harbor `--agent` (`openhands-sdk`, `openhands`, `mini-swe-agent`, or `module:Class`) |
| `OPENHANDS_TOOLS` | `terminal` | Comma-separated OpenHands tools (`terminal,file_editor,task_tracker`) |

To run rollouts inside **Snowflake Cortex Sandboxes** (`--env snowflake`), install `harbor[snowflake]` and set:

```bash
export HARBOR_ENV=snowflake
```

See the [Arctic Platform Harbor RL README](https://github.com/Snowflake-AI-Research/Arctic-Platform/tree/karthik/openhands-harbor/recipes/rl/harbor) for full setup instructions, SWE-smith code localization reproduction, and reference convergence curves.
