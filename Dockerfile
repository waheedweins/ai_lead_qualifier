FROM python:3.11-slim

# Prevent Python from buffering stdout/stderr (critical for CloudWatch logs)
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
# Ensure `src` package is importable from /app
ENV PYTHONPATH=/app

WORKDIR /app

# Install system deps needed by psycopg2-binary and curl (for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (layer-cached separately from code)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy full project
COPY . .

EXPOSE 8000

# FIXED: was "api:app" which is wrong — correct module path is src.app.main:app
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]

# Healthcheck using /health/  (matches the router prefix)
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=5 \
    CMD curl -f http://localhost:8000/health/ || exit 1
