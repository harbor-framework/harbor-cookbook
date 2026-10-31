#!/bin/sh
set -eu

snapshot_tmp=$(mktemp /snapshot/state.XXXXXX)
trap 'rm -f "$snapshot_tmp"' EXIT HUP INT TERM

psql -X -A -t -v ON_ERROR_STOP=1 -U postgres -d orders \
    -f /opt/recipe/capture.sql > "$snapshot_tmp"
mv "$snapshot_tmp" /snapshot/state.json
