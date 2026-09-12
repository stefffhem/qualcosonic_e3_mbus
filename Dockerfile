FROM python:3.11-alpine

RUN apk add --no-cache \
    build-base \
    python3-dev \
    musl-dev \
    libffi-dev \
    openssl-dev

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY run.sh .
COPY qualcosonic_mbus_reader.py .
RUN chmod +x /app/run.sh

CMD ["/app/run.sh"]
