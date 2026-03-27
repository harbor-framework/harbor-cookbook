# skills

Giving agents access to custom skills via the `skills_dir` setting in `task.toml`.

## Structure

```
skills/
├── README.md
├── task.toml                  # skills_dir declared under [environment]
├── instruction.md             # Agent prompt
├── environment/
│   ├── Dockerfile             # Agent container; copies skills into /skills
│   └── skills/
│       └── generate-greeting/
│           └── SKILL.md       # Skill definition (YAML frontmatter + instructions)
├── tests/
│   ├── test.sh                # Verifier entrypoint
│   └── test_greeting.py       # Pytest tests
└── solution/
    └── solve.sh               # Reference solution
```

## How it works

The `skills_dir` key under `[environment]` in `task.toml` tells Harbor where to find skill definitions inside the container. At startup, Harbor copies every subdirectory from that path into the agent's native skills directory (e.g. `~/.claude/skills/` for Claude Code).

Each skill is a subdirectory containing a `SKILL.md` file with YAML frontmatter (`name`, `description`) followed by Markdown instructions. The agent discovers and invokes these skills like any other built-in skill.

The Dockerfile copies the local `skills/` directory into the container at `/skills`, and `task.toml` sets `skills_dir = "/skills"` so Harbor knows to pick them up.

## Run

```bash
harbor run -p harbor_cookbook/recipes/skills --agent claude-code --model anthropic/claude-sonnet-4-6
```
