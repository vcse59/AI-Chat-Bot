# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000 \
    HOST=0.0.0.0

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# Copy dependency files
COPY pyproject.toml requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir fastapi[all] uvicorn[standard] \
    && pip install --no-cache-dir sqlalchemy databases[sqlite] \
    && pip install --no-cache-dir openai websockets email-validator pytz

# Copy application code
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p /app/data /app/logs \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Create SQLite database directory with proper permissions
RUN mkdir -p /app/data

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE $PORT

# Default command - run uvicorn directly with the app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]