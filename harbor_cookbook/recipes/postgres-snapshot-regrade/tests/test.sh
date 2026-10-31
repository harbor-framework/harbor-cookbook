#!/bin/bash
set -euo pipefail

uv venv --python 3.13.17 /tmp/recipe-verifier
uv pip install --python /tmp/recipe-verifier/bin/python \
    pytest==8.4.1 pytest-json-ctrf==0.3.5

# Dependency failures above are infrastructure errors, not a zero task score.
if /tmp/recipe-verifier/bin/python -m pytest \
    --ctrf /logs/verifier/ctrf.json /tests/test_snapshot.py -rA; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi
