FROM ubuntu:24.04

RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    && rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY blocked-domains.txt /etc/blocked-domains.txt
COPY block-server.py /usr/local/bin/block-server.py

ENTRYPOINT ["/entrypoint.sh"]
WORKDIR /app
