# cortex_rl

Go from any [Harbor](https://github.com/harbor-framework/harbor) evaluation tasks to RL post-training on **Snowflake Cortex Training** in two environment variables (`TRAIN_HARBOR_TASKS` and `EVAL_HARBOR_TASKS`).

Every Harbor task already defines the three pieces an RL rollout needs:
1. `instruction.md`: the prompt shown to the agent.
2. `environment/`: the sandbox (`--env snowflake`, `docker`, `modal`, `daytona`, or `HostEnvironment`).
3. `tests/test.sh`: the verifier that writes `/logs/verifier/reward.txt` or `/logs/verifier/reward.json`.

Cortex Training's Harbor integration (`arctic_platform.integrations.harbor`) wires Harbor's `Trial` and `Verifier` directly into an online GSPO/GRPO loop — no custom rollout adapter, reward wrapper, or local GPUs required. Point at your Harbor task directories, tweak `recipes/rl/harbor/run_qwen35_4b.sh` (or let the [`cortex-training-rl`](https://github.com/OpenHands/extensions/pull/771) skill configure and launch it for you), and run from a CPU driver machine while Cortex Training handles distributed vLLM sampling and FSDP/Megatron policy updates on remote H200 GPUs.

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

### 3. Launch `recipes/rl/harbor/run_qwen35_4b.sh`

`recipes/rl/harbor/run_qwen35_4b.sh` is a self-contained ~200-line launch script that automatically discovers every Harbor task under `TRAIN_HARBOR_TASKS` and `EVAL_HARBOR_TASKS`, builds the dataset parquets, spins up per-rollout OpenAI proxies + Harbor trials (`64` concurrent rollouts/step), grades each trial with Harbor's `Verifier`, and updates the model weights:

```bash
export RUN_NAME=qwen35-4b-harbor-rl-$(date +%m%d-%H%M)
export CKPT_DIR=$HOME/checkpoints/$RUN_NAME
export HARBOR_SKILL=/path/to/SKILL.md   # optional: ":"-separated OpenHands SKILL.md paths
export ARCTIC_CORTEX_JOB_COMMENT="<your name> harbor rl"
export LOGGER=console OPENHANDS_WORKSPACE=/tmp/harbor-ws STARTUP_TIMEOUT=14400
mkdir -p "$CKPT_DIR"

bash recipes/rl/harbor/run_qwen35_4b.sh trainer.max_training_steps=50
```

## Tweak `run_qwen35_4b.sh` for your model, agent, or sandbox

Everything in [`recipes/rl/harbor/run_qwen35_4b.sh`](https://github.com/Snowflake-AI-Research/Arctic-Platform/blob/karthik/openhands-harbor/recipes/rl/harbor/run_qwen35_4b.sh) can be overridden via environment variables or Hydra CLI arguments (`"$@"`) passed at the end of the command — no Python code changes needed:

| Variable | Default in `run_qwen35_4b.sh` | What to tweak |
| :--- | :--- | :--- |
| `TRAIN_HARBOR_TASKS` | — | Directory of training Harbor tasks (`instruction.md` + `environment/` + `tests/test.sh`) |
| `EVAL_HARBOR_TASKS` | `TRAIN_HARBOR_TASKS` | Directory of evaluation Harbor tasks |
| `MODEL` | `Qwen/Qwen3.5-4B` | Any HuggingFace model ID (`Qwen/Qwen3-8B`, `Qwen/Qwen2.5-Coder-7B-Instruct`, etc.) |
| `NUM_TRAIN_GPUS` / `NUM_SAMPLING_ENGINES` | `4` / `4` | Remote Cortex H200 GPUs allocated to FSDP training vs. vLLM rollout sampling |
| `BATCH_SIZE` / `N_ROLLOUTS` | `8` / `8` | Prompts per step $\times$ rollouts per prompt (`64` concurrent Harbor trials/step) |
| `MAX_TURNS` / `MAX_CONTEXT_LENGTH` | `10` / `32768` | Max agent tool turns per trial and token context window |
| `LR` | `1.0e-6` | Policy learning rate (plus any SkyRL Hydra flag like `trainer.algorithm.advantage_estimator=grpo`) |
| `HARBOR_SKILL` | — | Optional `:`-separated `SKILL.md` file(s) or skill directories injected into the agent |
| `HARBOR_ENV` | `HostEnvironment` | Any Harbor `--env` provider (`snowflake`, `docker`, `modal`, `daytona`, `e2b`, etc.) |
| `HARBOR_AGENT` | `OpenHandsHarborAgent` | Any Harbor `--agent` (`openhands-sdk`, `openhands`, `mini-swe-agent`, or `module:Class`) |
| `OPENHANDS_TOOLS` | `terminal` | Comma-separated OpenHands tools (`terminal,file_editor,task_tracker`) |
| `OPENHANDS_SYSTEM_PROMPT_FILE` | built-in prompt | Custom system prompt file for the agent |

For example, to train a different model with `SnowflakeSandboxEnvironment` (`--env snowflake`), `file_editor` enabled, and 15 max turns:

```bash
MODEL=Qwen/Qwen3-8B \
HARBOR_ENV=snowflake \
OPENHANDS_TOOLS=terminal,file_editor \
MAX_TURNS=15 \
bash recipes/rl/harbor/run_qwen35_4b.sh trainer.max_training_steps=100
```

## Use the `cortex-training-rl` skill to configure, launch, and monitor runs

Instead of editing flags by hand, you can install the **[`cortex-training-rl`](https://github.com/OpenHands/extensions/pull/771)** agent skill (available in [`OpenHands/extensions/skills/cortex-training-rl`](https://github.com/OpenHands/extensions/pull/771) or via `/cortex-training-rl` in OpenHands / Claude Code / Cursor):

- **Auto-configures `run_qwen35_4b.sh`:** Tell your coding agent which Harbor task directory, model, sandbox (`--env snowflake`, `docker`, `HostEnvironment`), or target `SKILL.md` you want to train with, and the skill sets up the environment variables, checks Cortex H200 capacity, and verifies the 128 MiB sequence-budget cap (`BATCH_SIZE * N_ROLLOUTS * MAX_CONTEXT_LENGTH`).
- **Launches & monitors detached training:** Starts `run_qwen35_4b.sh` in a detached session, tails per-step rewards and `.error` counts across `trajectories/step_*/`, and plots the live reward convergence curve (`reward_graph.svg`).
- ** Cleans up Cortex GPU jobs:** Automatically cancels remote training/sampling sub-jobs when your run finishes so no GPUs are left idle.

See the [Arctic Platform Harbor RL README](https://github.com/Snowflake-AI-Research/Arctic-Platform/tree/karthik/openhands-harbor/recipes/rl/harbor) for full setup instructions, SWE-smith code localization reproduction, and reference convergence curves.
