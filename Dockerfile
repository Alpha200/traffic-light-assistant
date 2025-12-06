# Build stage for frontend
FROM node:22-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend files
COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Backend stage
FROM python:3.14-slim

WORKDIR /app

# Install system dependencies and nginx
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --only main --no-root

# Copy backend code
COPY main.py ./

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/frontend/dist ./static

# Copy app directory
COPY app ./app

# Copy nginx config
COPY nginx.conf /etc/nginx/sites-available/default

# Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Define volume for DuckDB persistence
VOLUME ["/app/data"]

# Expose port
EXPOSE 8000

# Run entrypoint
CMD ["/app/entrypoint.sh"]
