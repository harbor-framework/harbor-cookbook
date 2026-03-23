#!/bin/bash
set -euo pipefail

# Route all task domains to the local matcher.
while IFS= read -r domain || [ -n "$domain" ]; do
  domain="${domain%%#*}"
  domain="${domain#"${domain%%[![:space:]]*}"}"
  domain="${domain%"${domain##*[![:space:]]}"}"
  [ -z "$domain" ] && continue
  echo "127.0.0.1 $domain" >> /etc/hosts
done < /etc/candidate-domains.txt

# Block server on port 80
python3 /usr/local/bin/block-server.py &

mkdir -p /logs/verifier
chmod 777 /logs /logs/verifier

exec "$@"
