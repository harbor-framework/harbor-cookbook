FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    xvfb \
    fluxbox \
    xterm \
    scrot \
    xdotool \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV DISPLAY=:99

WORKDIR /app

COPY server.py .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 8000

CMD ["./entrypoint.sh"]
