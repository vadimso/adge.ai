FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir fastapi uvicorn google-cloud-storage google-cloud-firestore google-auth

ENV PORT=8080

CMD ["python", "worker.py"]