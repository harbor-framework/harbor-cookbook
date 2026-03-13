FROM python:3.12-slim

WORKDIR /app

RUN pip install flask

COPY server.py .

EXPOSE 5000

CMD ["python", "server.py"]
