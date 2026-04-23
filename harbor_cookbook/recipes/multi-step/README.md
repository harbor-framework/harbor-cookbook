# multi-step

A multi-step Harbor task: the agent progresses through three ordered steps
(scaffold → implement → document) against a shared container, with per-step
instructions, tests, workdir uploads, verifier env vars, healthcheck, and
artifact collection. Demonstrates early stopping via `min_reward` and reward
aggregation via `multi_step_reward_strategy`.

## Structure

```
multi-step/
├── README.md
├── task.toml                    # schema_version = "1.1", [[steps]] entries, artifacts
├── environment/
│   └── Dockerfile               # Ubuntu 24.04, shared across all steps
├── tests/
│   └── helpers.sh               # Shared helpers merged into /tests for each step
└── steps/
    ├── scaffold/                # Step 1: create /app/greet.sh that prints "hello"
    │   ├── instruction.md
    │   ├── tests/test.sh
    │   └── solution/solve.sh
    ├── implement/               # Step 2: read /app/config.txt, print "Hello, <name>!"
    │   ├── instruction.md
    │   ├── workdir/             # Uploaded to WORKDIR before the agent runs
    │   │   ├── config.txt       # Step-specific fixture
    │   │   └── setup.sh         # Reserved filename: runs pre-agent, then self-deletes
    │   ├── tests/
    │   │   ├── test.sh          # Uses step-scoped [steps.verifier.env]
    │   │   └── expected.txt     # Step-local fixture
    │   └── solution/solve.sh
    └── document/                # Step 3: write /app/README.md describing the CLI
        ├── instruction.md
        ├── tests/test.sh
        └── solution/solve.sh
```

## What each step-level feature demonstrates

- **Shared helpers** — `tests/helpers.sh` at the task root is uploaded to
  `/tests/helpers.sh` for every step; each step's `test.sh` sources it.
- **Per-step workdir uploads** — `steps/implement/workdir/config.txt` is
  placed in WORKDIR before the agent runs (only for the implement step).
- **`workdir/setup.sh` hook** — reserved filename that runs as the agent user
  from WORKDIR after the upload and before the agent starts. Self-deletes on
  its last line so the agent's WORKDIR stays clean.
- **Per-step healthcheck** — implement step pre-flight checks that scaffold's
  `greet.sh` is in place before the agent starts.
- **Per-step verifier env** — implement step sets `EXPECTED_NAME` and
  `EXPECTED_GREETING` scoped to its verifier only.
- **Early stopping (`min_reward`)** — scaffold requires `1.0` (no point
  proceeding without a working script); implement accepts `0.5`.
- **Per-step artifacts** — task-level `/app/greet.sh` is snapshotted every
  step; `/app/README.md` is snapshotted only after the document step.

## Run

```bash
harbor run -p harbor_cookbook/recipes/multi-step --agent claude-code --model anthropic/claude-sonnet-4-6
```

Sanity-check with the Oracle agent, which runs each step's `solve.sh` in order:

```bash
harbor run -p harbor_cookbook/recipes/multi-step --agent oracle
```

Trial reward should be `1.0` under the default `multi_step_reward_strategy =
"mean"`.
