#!/bin/bash

for domain in example.com google.com wikipedia.org; do
  if curl -s --connect-timeout 5 "http://$domain" -o /dev/null 2>&1; then
    echo "$domain"
  fi
done | sort > /app/reachable.txt
