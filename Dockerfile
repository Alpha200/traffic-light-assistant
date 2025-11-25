# Build stage for frontend
FROM node:22-alpine as frontend-builder

WORKDIR /app/frontend

# Copy frontend files
COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# Backend stage
FROM python:3.14-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

# Copy backend code
COPY main.py ./

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/frontend/dist ./static

# Copy app directory
COPY app ./app

# Define volume for DuckDB persistence
VOLUME ["/app/data"]

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]
