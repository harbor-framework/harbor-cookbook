FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_PRERELEASE=allow

WORKDIR /app

COPY server.py .
COPY challenge.py .

EXPOSE 8000

CMD ["uv", "run", "server.py"]
