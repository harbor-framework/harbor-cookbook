# Pattern-Based Host Blocking

This container has hostname blacklisting enforced by a local HTTP gateway. Some domains return a blocked response instead of a successful one.

Your task:

1. Test which of the following domains return a successful HTTP response (status code 2xx): `example.com`, `google.com`, `python.org`, `docs.python.org`, `shop-42.example.net`, `shop.example.net`
2. Write only the accessible domains (one per line, sorted alphabetically) to `/app/accessible.txt`. Do not include blocked domains that return error responses.
