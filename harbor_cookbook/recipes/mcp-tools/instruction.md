# MCP Tools Task

There is an MCP server running at `http://mcp-server:8000/mcp` that exposes two tools:

- `get_secret` — returns a secret value
- `get_timestamp` — returns the server's startup timestamp

Your task:

1. Connect to the MCP server
2. Call both tools
3. Write the secret to `/app/secret.txt`
4. Write the timestamp to `/app/timestamp.txt`

Write each value exactly as returned by the tool, with no additional formatting.
