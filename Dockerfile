%%writefile Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the port (match the one used by uvicorn)
EXPOSE 8000

# Start the server on 0.0.0.0 so it's reachable externally
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]

# Optional: internal container healthcheck for Docker (AWS will use ALB health check instead)
HEALTHCHECK --interval=30s --timeout=10s CMD curl -f http://localhost:8000/health || exit 1
