#!/bin/bash

for domain in example.com google.com wikipedia.org; do
  if getent hosts "$domain" > /dev/null 2>&1; then
    echo "$domain"
  fi
done > /app/resolved.txt
