#!/bin/bash

sum=0
while IFS= read -r line; do
  sum=$((sum + line))
done < /app/data.txt

echo "$sum" > /app/result.txt
