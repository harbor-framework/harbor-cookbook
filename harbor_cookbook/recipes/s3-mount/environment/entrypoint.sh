#!/bin/bash
set -euo pipefail

aws s3 cp "$S3_DATA_URI" /app/data.txt

exec "$@"
