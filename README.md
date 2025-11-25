# Traffic Light Assistant

Track and measure traffic lights with precise schedule capture. Built with FastAPI + DuckDB and Vue.js 3.

## Features

- ➕ Add traffic lights with location, coordinates, and notes
- 📋 View all traffic lights in a list
- ⏱️ Capture green light duration with millisecond precision
- 📊 View captured schedules for each traffic light
- 🗑️ Delete traffic lights and schedules
- 🌙 Dark theme, mobile-optimized design
- 🔐 OpenID Connect authentication

## Quick Start

### Prerequisites
- Python 3.14+
- Node.js 18+

### Setup

**Backend with environment variables:**
```bash
poetry install
cp .env.example .env  # Configure OIDC settings
./run.sh
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` - API docs at `http://localhost:8000/docs`

## Configuration

Set these environment variables (or use `.env` file with `./run.sh`):
- `OIDC_PROVIDER_URL` - OpenID Connect provider URL
- `OIDC_CLIENT_ID` - Client ID for OIDC
- `OIDC_AUDIENCE` - Audience/scope for tokens
- `OIDC_ISSUER` - Token issuer (optional, defaults to provider_url)

## Database

Uses DuckDB (auto-created as `traffic_lights.duckdb`)

## Tech Stack

- **Backend:** FastAPI, DuckDB, httpx, python-jose
- **Frontend:** Vue.js 3, Vue Router, Vite