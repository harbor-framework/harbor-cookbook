Create a file `/app/deduplicate.py` containing a function `deduplicate(records)`.

**Input:** A list of dicts, each with at least `"id"` (int) and `"email"` (str) keys (may have other keys too).

**Behavior:** Remove duplicate emails (case-insensitive), keeping only the record with the highest `"id"` for each email. Return the deduplicated list sorted by `"id"` ascending.

**Example:**

```python
records = [
    {"id": 1, "email": "alice@example.com", "name": "Alice"},
    {"id": 2, "email": "bob@example.com", "name": "Bob"},
    {"id": 3, "email": "ALICE@example.com", "name": "Alice A."},
]

deduplicate(records)
# => [{"id": 2, "email": "bob@example.com", "name": "Bob"},
#     {"id": 3, "email": "ALICE@example.com", "name": "Alice A."}]
```

Your solution should handle large datasets (100k+ records) efficiently.
