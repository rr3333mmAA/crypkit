FROM python:3.13.2-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y netcat-traditional && \
    apt-get clean && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["/app/start.sh"]