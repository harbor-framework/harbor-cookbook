#!/bin/bash

while IFS= read -r domain || [ -n "$domain" ]; do
  [ -z "$domain" ] && continue
  if curl -sf --connect-timeout 5 "http://$domain" -o /dev/null 2>&1; then
    echo "$domain"
  fi
done < /etc/candidate-domains.txt | sort > /app/accessible.txt
