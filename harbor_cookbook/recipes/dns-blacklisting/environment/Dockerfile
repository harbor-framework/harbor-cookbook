FROM ubuntu:24.04

RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# Pre-install verifier deps
RUN curl -LsSf https://astral.sh/uv/0.9.7/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"
RUN uvx --with pytest==8.4.1 --with pytest-json-ctrf==0.3.5 pytest --version

RUN mkdir -p /app

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY blocked-domains.txt /etc/blocked-domains.txt
COPY block-server.py /usr/local/bin/block-server.py

ENTRYPOINT ["/entrypoint.sh"]
WORKDIR /app
