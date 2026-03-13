#!/bin/bash

# Add the "harbor" item
curl -s -X POST http://api-server:5000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "harbor"}'

# Fetch the updated list and save it
curl -s http://api-server:5000/items > /app/items.json
