#!/bin/bash

cat > /app/deduplicate.py << 'EOF'
def deduplicate(records):
    best = {}
    for record in records:
        key = record["email"].lower()
        if key not in best or record["id"] > best[key]["id"]:
            best[key] = record
    return sorted(best.values(), key=lambda r: r["id"])
EOF
