#!/bin/bash
set -e

# Start FastAPI backend
python /app/main.py &
BACKEND_PID=$!

# Wait for backend to be ready
sleep 2

# Start nginx in foreground
nginx -g "daemon off;"
