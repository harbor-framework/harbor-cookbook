# s3-mount

Provisioning S3 data into an agent container at startup using an entrypoint that downloads via the AWS CLI.

## Structure

```
s3-mount/
├── README.md
├── task.toml              # Timeouts, resources, AWS env vars
├── instruction.md         # What the agent should do
├── environment/
│   ├── Dockerfile           # Installs AWS CLI, sets entrypoint
│   ├── docker-compose.yaml  # Injects AWS env vars into the container
│   └── entrypoint.sh       # Downloads from S3 before agent starts
├── tests/
│   ├── test.sh            # Installs pytest, runs tests, writes reward
│   └── test_solution.py   # Pytest assertions
└── solution/
    └── solve.sh           # Reference solution
```

## How it works

The Dockerfile installs the AWS CLI and sets `entrypoint.sh` as the container's ENTRYPOINT. When the container starts, the entrypoint downloads the file at `$S3_DATA_URI` to `/app/data.txt`, then hands off to Harbor via `exec "$@"`. By the time the agent starts, the data is already on disk — the agent never interacts with S3 directly.

AWS credentials and the S3 URI are declared in `[environment.env]` in `task.toml`, which resolves them from the host environment at runtime. The `docker-compose.yaml` explicitly lists these variables in its `environment:` section so they are injected into the container at creation time (Harbor's base compose config does not forward `[environment.env]` vars to the container process — only to `exec` calls).

## Setup

### 1. Create an S3 bucket and upload sample data

```bash
aws s3 mb s3://harbor-s3-example
printf "10\n20\n30\n40\n50\n" | aws s3 cp - s3://harbor-s3-example/numbers.txt
```

### 2. Export AWS credentials

```bash
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
```

## Run

```bash
harbor run -p harbor_cookbook/recipes/s3-mount --agent claude-code --model anthropic/claude-sonnet-4-6
```

To use a different S3 path:

```bash
S3_DATA_URI=s3://my-bucket/my-file.txt harbor run -p harbor_cookbook/recipes/s3-mount --agent claude-code --model anthropic/claude-sonnet-4-6
```
