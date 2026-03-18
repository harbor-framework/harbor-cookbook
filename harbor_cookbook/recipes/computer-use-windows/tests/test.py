"""Tests that the agent completed the multi-step GUI challenge."""

import os
import sys

SECRET_VALUE = "HARBOR-CU-2025-VERIFIED"

# Support both Windows (Daytona) and Linux (Docker oracle) paths
SECRET_PATHS = [r"C:\app\secret.txt", "/app/secret.txt"]
REWARD_PATHS = [r"C:\logs\verifier\reward.txt", "/logs/verifier/reward.txt"]


def find_existing(paths):
    for p in paths:
        if os.path.exists(p):
            return p
    return paths[0]


def run_tests():
    errors = []

    secret_path = find_existing(SECRET_PATHS)
    if not os.path.exists(secret_path):
        errors.append(f"secret.txt was not created at any of {SECRET_PATHS}")
    else:
        with open(secret_path) as f:
            content = f.read().strip()
        if content != SECRET_VALUE:
            errors.append(f"secret.txt contains '{content}', expected '{SECRET_VALUE}'")

    reward = "1" if not errors else "0"

    reward_path = find_existing(REWARD_PATHS)
    os.makedirs(os.path.dirname(reward_path), exist_ok=True)
    with open(reward_path, "w") as f:
        f.write(reward)

    if errors:
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)
    else:
        print("PASS: secret.txt matches expected value")


if __name__ == "__main__":
    run_tests()
