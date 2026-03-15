FROM python:3.12-slim

WORKDIR /app

RUN pip install "fastmcp>=3.0" "anthropic>=0.52"

COPY server.py persona.md .

EXPOSE 8000

CMD ["python", "server.py"]
