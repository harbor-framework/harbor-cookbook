# PostgreSQL snapshot and regrade

This recipe demonstrates grading a database task from a recorded artifact.
The agent repairs order totals in a PostgreSQL sidecar. A collect hook captures
the resulting rows as JSON, and a separate verifier grades that snapshot.
The same saved trial can then be regraded after the original containers have
been deleted, without running the agent or database again.

The repair is deliberately small: three incorrect totals, one empty order,
and one already correct order. The example teaches artifact collection and
regrading, rather than measuring difficult SQL problem solving.

## How it works

1. Docker Compose starts `main` with `psql` and a `database` sidecar with
   PostgreSQL 17.11. Connection settings are provided through `PG*`
   environment variables. The database has no published host port.
2. The agent can read the three tables and update only `orders.total_cents`.
   The database's `pg_hba.conf` permits remote connections only for this
   restricted role. The initialization password is a demo value; it cannot
   be used to connect remotely as the database superuser.
3. After the agent finishes, Harbor stops `main`. The sidecar
   `[[verifier.collect]]` hook then runs `capture-state` as `postgres` using a
   local Unix socket. One SQL statement captures all grading inputs from a
   consistent database snapshot, with deterministic row ordering. The script
   renames the output into place only after the query succeeds.
4. The artifact declaration names both its absolute path and service:

   ```toml
   artifacts = [{ source = "/snapshot/state.json", service = "database" }]
   ```

   Harbor records the file and its artifact manifest in the trial directory.
   It restores the file at `/snapshot/state.json` in the separate verifier
   built from `tests/Dockerfile`.
5. The verifier checks the saved rows, including the zero-total case and
   preservation of other data. It has no PostgreSQL client or server and
   makes no connection to the original database. Test dependencies are
   installed by `tests/test.sh`, so the verifier needs internet access for
   installation.
6. `harbor trial regrade` creates a new trial from the recorded artifacts and
   runs the verifier again. It leaves the source trial unchanged and does
   not rerun the collect hook against a live database.

Keeping the artifact as JSON also lets the verifier inspect data without
executing a SQL dump. For a larger task, include every piece of state needed
by its verifier in the capture query; unrecorded database state cannot be
recovered later by regrading.

## Run without model credentials

Requirements: Docker with Compose and [uv](https://docs.astral.sh/uv/).
Run these commands from the repository root. They use released Harbor 0.24.0
and Python 3.13.17.

```bash
recipe=harbor_cookbook/recipes/postgres-snapshot-regrade
runs=$(mktemp -d)

# The reference solution repairs all totals: expected reward 1.
uvx --python 3.13.17 --from 'harbor==0.24.0' harbor run \
  -p "$recipe" -a oracle -e docker --jobs-dir "$runs" --job-name oracle

# An agent that does nothing leaves three incorrect totals: expected reward 0.
uvx --python 3.13.17 --from 'harbor==0.24.0' harbor run \
  -p "$recipe" -a nop -e docker --jobs-dir "$runs" --job-name nop
```

Both jobs use Harbor's default environment cleanup. A reward of zero from
Nop is expected; an exception or missing reward is an infrastructure failure.
The verifier writes test details to `verifier/ctrf.json` and its score to
`verifier/reward.txt` inside each trial directory.

## Regrade the saved trial

Select the single Oracle trial, rather than the parent job directory:

```bash
source_trial=$(python3 - "$runs/oracle" <<'PY'
from pathlib import Path
import sys

trials = list(Path(sys.argv[1]).glob("*/result.json"))
assert len(trials) == 1, f"Expected one trial, found {len(trials)}"
print(trials[0].parent)
PY
)

# Inspect the manifest to see which service supplied the recorded artifact.
cat "$source_trial/artifacts/manifest.json"

uvx --python 3.13.17 --from 'harbor==0.24.0' harbor trial regrade \
  "$source_trial" -p "$recipe" -e docker \
  --trials-dir "$runs/regraded" --trial-name oracle-regraded
```

The regraded trial should also receive reward **1**, even though the original
database no longer exists. Repeating the selection with `$runs/nop` and using
a different `--trial-name` should preserve reward **0**.

Keep the complete source trial directory, including its manifest and artifact
files. A missing required snapshot is a regrade error. The manifest maps saved
files to their service and original path; the verifier reads
`/snapshot/state.json`, not a guessed path beneath the host trial directory.

To try a revised verifier, edit only `tests/` and regrade into a new output
directory. Compare both trials' CTRF reports to see how the grading changed,
while keeping the original agent output and snapshot intact.
