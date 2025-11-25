# Use Python 3.11 slim image as base
FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update -o Acquire::AllowInsecureRepositories=true -o Acquire::AllowDowngradeToInsecureRepositories=true \
    && apt-get install -y \
        postgresql-client \
        netcat-openbsd \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Create directories for static and media files AND set permissions on start.sh
# We keep chmod +x here even though the volume might override it, for best practice
RUN mkdir -p /app/static /app/media && \
    chmod +x /app/start.sh

# Expose port
EXPOSE 8000

# Default CMD (overridden by docker-compose)
CMD ["/bin/sh", "/app/start.sh"]