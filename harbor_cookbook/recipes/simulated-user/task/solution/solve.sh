#!/bin/bash

cat > /app/convert.py << 'EOF'
import csv
import json
import sys

reader = csv.DictReader(sys.stdin)
print(json.dumps(list(reader)))
EOF
