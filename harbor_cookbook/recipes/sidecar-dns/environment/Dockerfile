FROM ubuntu:24.04

RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    gosu \
    && rm -rf /var/lib/apt/lists/*

# Pre-install verifier deps
RUN curl -LsSf https://astral.sh/uv/0.9.7/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"
RUN uvx --with pytest==8.4.1 --with pytest-json-ctrf==0.3.5 pytest --version

RUN useradd -m -s /bin/bash agent

RUN mkdir -p /app && chown agent:agent /app

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY block-server.py /usr/local/bin/block-server.py

ENTRYPOINT ["/entrypoint.sh"]
WORKDIR /app
