FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv (respects lockfile)
RUN uv sync --frozen --no-dev --no-install-project

# Copy application code
COPY src/ ./src/
COPY manifest.json .

# Create logs directory
RUN mkdir -p /app/logs

# Expose ports
EXPOSE 10821 9091

# Set environment variables
ENV PYTHONPATH=/app/src
ENV LOG_LEVEL=INFO
ENV PROMETHEUS_PORT=9091
ENV MCP_TRANSPORT=http
ENV MCP_PORT=10821

# Activate the venv in PATH
ENV PATH="/app/.venv/bin:$PATH"

# Run in HTTP mode using the transport module (respects MCP_TRANSPORT env var)
CMD ["python", "-m", "tailscalemcp", "--http"]
