# Single-Container DNS

This container has domain blacklisting enforced via `/etc/hosts`. You are running as a non-root user and cannot modify the network configuration.

Your task:

1. Test which of the following domains are reachable: `example.com`, `google.com`, `wikipedia.org`
2. Write each reachable domain on its own line (sorted alphabetically) to `/app/reachable.txt`
