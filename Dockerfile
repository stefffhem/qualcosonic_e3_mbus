FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY qualcosonic_mbus_reader.py .
COPY run.sh .
RUN chmod +x /app/run.sh

CMD ["/app/run.sh"]

