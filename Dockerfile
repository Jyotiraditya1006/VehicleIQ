FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for build tools and PostgreSQL adapter
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV INGESTION_MODE=simulation
ENV DB_TYPE=sqlite
ENV SQLITE_DB_PATH=/app/data/vehicleiq.db

# Ensure data directory exists for SQLite volume mount
RUN mkdir -p /app/data

CMD ["python", "main.py", "--mode", "simulation", "--scenario", "city_driving", "--count", "100"]
