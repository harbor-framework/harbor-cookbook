FROM python:3.12-slim

WORKDIR /app

RUN pip install "fastmcp>=3.0"

COPY server.py .

EXPOSE 8000

CMD ["python", "server.py"]
