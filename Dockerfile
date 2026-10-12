# Dockerfile for Flask backend
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (if any needed for pandas, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy Python source files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose Flask default port
EXPOSE 5000

# Use gunicorn for production (fallback to flask run for dev)
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
