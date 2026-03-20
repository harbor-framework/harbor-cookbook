#!/bin/bash
set -e

# Block domains via /etc/hosts
while IFS= read -r domain || [ -n "$domain" ]; do
  [ -z "$domain" ] && continue
  echo "127.0.0.1 $domain" >> /etc/hosts
  echo "127.0.0.1 www.$domain" >> /etc/hosts
done < /etc/blocked-domains.txt

# Block server on port 80
python3 /usr/local/bin/block-server.py &

mkdir -p /logs/verifier
chmod 777 /logs /logs/verifier

exec "$@"
