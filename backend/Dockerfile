FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
# gcc and libpq-dev are often needed for psycopg2 (backend driver)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Command is handled by docker-compose to run migrations first
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
