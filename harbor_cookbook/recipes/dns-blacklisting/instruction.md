# Single-Container DNS

This container has domain blacklisting enforced via `/etc/hosts`. Some domains are blocked and will not return a successful HTTP response.

Your task:

1. Test which of the following domains return a successful HTTP response (status code 2xx): `example.com`, `google.com`, `wikipedia.org`
2. Write only the accessible domains (one per line, sorted alphabetically) to `/app/accessible.txt`. Do not include blocked domains that return error responses.
