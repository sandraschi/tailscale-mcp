FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
COPY pyproject.toml .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir prometheus-client structlog

# Copy application code
COPY src/ ./src/
COPY manifest.json .

# Create logs directory
RUN mkdir -p /app/logs

# Expose ports
EXPOSE 8080 9091

# Set environment variables
ENV PYTHONPATH=/app/src
ENV LOG_LEVEL=INFO
ENV PROMETHEUS_PORT=9091

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:9091/metrics || exit 1

# Run the application
CMD ["python", "-m", "tailscalemcp"]