# Multi-Container Task

There is a REST API running at `http://api-server:5000`.

The API has the following endpoints:

- `GET /items` — returns a JSON list of items
- `POST /items` — accepts `{"name": "..."}` and creates a new item

Your task:

1. Fetch the current list of items from the API
2. Add a new item with the name `"harbor"`
3. Fetch the updated list and write it to `/app/items.json`

The file should contain the JSON response exactly as returned by the API.
