# prime_rl

RL training on Harbor tasks using [Prime RL](https://docs.primeintellect.ai/prime-rl).

This directory is a pointer. The full environment integration lives in the verifiers repo:

**[verifiers/environments/opencode_harbor](https://github.com/PrimeIntellect-ai/verifiers/tree/main/environments/opencode_harbor)**

## Quick start

Set up your workspace:

```bash
prime lab setup --prime-rl
```

Configure your environment TOML to use the `opencode_harbor` environment, then launch training:

```bash
prime lab start
```

See the [opencode_harbor README](https://github.com/PrimeIntellect-ai/verifiers/tree/main/environments/opencode_harbor) for full setup instructions.
