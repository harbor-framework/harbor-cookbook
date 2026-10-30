# cortex_rl

You have iterated on your agent harness (prompts, tools, `SKILL.md`), evaluated it with `harbor run`, and scaled up a directory of Harbor tasks. **Now you want to train the model weights inside that exact harness and environment.**

With [Snowflake Cortex Training](https://github.com/Snowflake-AI-Research/Arctic-Platform/tree/main/recipes/rl/harbor), you do not rewrite your Harbor tasks, agent harness, or verifier into an RL-specific format. Every Harbor task directory (`instruction.md` + `environment/` + `tests/test.sh`) is **already** an online RL environment:

- **Same agent & harness:** The exact agent (`--agent`), tools (`OPENHANDS_TOOLS`), system prompt (`OPENHANDS_SYSTEM_PROMPT_FILE`), and skills (`HARBOR_SKILL`) you evaluated in Harbor run during RL rollouts.
- **Same sandboxes & verifiers:** Harbor's `Trial` and `Verifier` execute each rollout inside your chosen `--env` (`snowflake`, `docker`, `modal`, `daytona`, or `HostEnvironment`) and read `/logs/verifier/reward.txt` or `reward.json`.
- **Zero local GPUs needed:** Run from your laptop or a lightweight CPU driver box. Cortex Training provisions remote H200 GPUs for distributed vLLM rollout sampling and FSDP/Megatron GSPO/GRPO policy updates, splicing multi-turn trajectories automatically via a per-rollout OpenAI proxy (`loss_mask = 1` on assistant turns, `0` on prompts and tool outputs).

This directory is a pointer. The full integration (`arctic_platform.integrations.harbor`) and recipe live in the Arctic Platform repo:

**[Arctic-Platform/recipes/rl/harbor](https://github.com/Snowflake-AI-Research/Arctic-Platform/tree/main/recipes/rl/harbor)**

---

## Go from `harbor run` (eval) to RL post-training in 3 commands

```bash
# 1. Authenticate to Snowflake Cortex Training (from any CPU machine)
cortex-training login ~/cortex-training-config.json

# 2. Point at the train and eval Harbor task directories you built/scaled
export TRAIN_HARBOR_TASKS=/path/to/train_harbor_tasks
export EVAL_HARBOR_TASKS=/path/to/eval_harbor_tasks
export HARBOR_SKILL=/path/to/SKILL.md   # optional: ":"-separated SKILL.md paths

# 3. Launch online GSPO/GRPO post-training
export ARCTIC_CORTEX_JOB_COMMENT="<your name> harbor rl"
bash recipes/rl/harbor/run_qwen35_4b.sh trainer.max_training_steps=50
```

`run_qwen35_4b.sh` automatically discovers every Harbor task under `TRAIN_HARBOR_TASKS` and `EVAL_HARBOR_TASKS`, builds the dataset parquets, runs `64` concurrent Harbor trials per step (`8 prompts × 8 rollouts`), grades each trial with Harbor's `Verifier`, updates the policy weights on remote H200 GPUs, and syncs weights back to the vLLM engines over NCCL.

---

## Two ways to customize your training run

### Option A: Let your coding agent drive via the `cortex-training-rl` skill (Recommended)

Install the **[`cortex-training-rl`](https://github.com/OpenHands/extensions/tree/main/skills/cortex-training-rl)** skill from `OpenHands/extensions` (or invoke `/cortex-training-rl` in OpenHands, Claude Code, or Cursor) and tell your agent what you want to train:

> *"Use `/cortex-training-rl` to post-train `Qwen/Qwen3-8B` on my Harbor tasks in `~/my-harbor-tasks/train` and `~/my-harbor-tasks/eval` with `HARBOR_SKILL=~/my-skill/SKILL.md`, `MAX_TURNS=15`, and `--env snowflake` for 50 steps."*

The skill knows the full [`recipes/rl/harbor/run_qwen35_4b.sh`](https://github.com/Snowflake-AI-Research/Arctic-Platform/blob/main/recipes/rl/harbor/run_qwen35_4b.sh) surface and handles the workflow end to end:
1. **Preflight & hyperparameter sizing:** Checks H200 capacity (`cortex-training capacity --hardware H200`), validates your Harbor task directories, and enforces the 128 MiB token-budget guard (`BATCH_SIZE * N_ROLLOUTS * MAX_CONTEXT_LENGTH`).
2. **Detached launch & live monitoring:** Starts `run_qwen35_4b.sh`, tails per-step rewards and `.error` counts across `trajectories/step_*/`, and generates `reward_graph.svg` to track convergence.
3. **Clean GPU teardown:** Cancels remote Cortex training and sampling sub-jobs when your run completes so no GPUs are left idle.

### Option B: Tweak `recipes/rl/harbor/run_qwen35_4b.sh` directly

[`recipes/rl/harbor/run_qwen35_4b.sh`](https://github.com/Snowflake-AI-Research/Arctic-Platform/blob/main/recipes/rl/harbor/run_qwen35_4b.sh) is a flat, self-contained ~200-line bash script. Every harness setting, sandbox backend, model, and RL hyperparameter is exposed as an environment variable (plus any SkyRL Hydra override passed as `"$@"`):

| What you want to change | Variable / Flag | Default | Example |
| :--- | :--- | :--- | :--- |
| **Task datasets** | `TRAIN_HARBOR_TASKS`, `EVAL_HARBOR_TASKS` | — | `~/tasks/train`, `~/tasks/eval` |
| **Agent skill (`SKILL.md`)** | `HARBOR_SKILL` | — | `~/skills/debug/SKILL.md:~/skills/git/SKILL.md` |
| **Agent tools** | `OPENHANDS_TOOLS` | `terminal` | `terminal,file_editor,task_tracker` |
| **Agent system prompt** | `OPENHANDS_SYSTEM_PROMPT_FILE` | built-in | `~/prompts/custom_agent.j2` |
| **Harbor agent class** | `HARBOR_AGENT` | `OpenHandsHarborAgent` | `my_pkg:MyAgent` (a Harbor `BaseAgent` that runs on the driver; agents installed inside the environment are refused) |
| **Harbor sandbox (`--env`)** | `HARBOR_ENV` | `HostEnvironment` | `snowflake`, `docker`, `modal`, `daytona`, `e2b` |
| **Base model** | `MODEL` | `Qwen/Qwen3.5-4B` | `Qwen/Qwen3-8B`, `Qwen/Qwen2.5-Coder-7B-Instruct` |
| **GPU allocation (train / sample)** | `NUM_TRAIN_GPUS` / `NUM_SAMPLING_ENGINES` | `4` / `4` | `8` / `8` |
| **Rollout concurrency** | `BATCH_SIZE` $\times$ `N_ROLLOUTS` | `8` $\times$ `8` (`64`/step) | `16` $\times$ `8` (`128`/step) |
| **Horizon & context length** | `MAX_TURNS` / `MAX_CONTEXT_LENGTH` | `10` / `32768` | `20` / `32768` |
| **Learning rate & RL loss** | `LR` / Hydra CLI args | `1.0e-6` (`gspo`) | `LR=5e-7 trainer.algorithm.policy_loss_type=grpo` |

Example tweaking model, sandbox, tools, and turn horizon in one command:

```bash
MODEL=Qwen/Qwen3-8B \
HARBOR_ENV=snowflake \
HARBOR_SKILL=~/skills/my_skill/SKILL.md \
OPENHANDS_TOOLS=terminal,file_editor \
MAX_TURNS=15 \
BATCH_SIZE=8 N_ROLLOUTS=8 \
bash recipes/rl/harbor/run_qwen35_4b.sh trainer.max_training_steps=100
```

See the [Arctic Platform Harbor RL README](https://github.com/Snowflake-AI-Research/Arctic-Platform/tree/main/recipes/rl/harbor) for full setup instructions, SWE-smith code localization reproduction, and reference convergence curves.
