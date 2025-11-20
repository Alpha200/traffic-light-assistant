# Traffic Light Assistant

Track and measure traffic lights with precise schedule capture. Built with FastAPI + DuckDB and Vue.js 3.

## Features

- ➕ Add traffic lights with location, coordinates, and notes
- 📋 View all traffic lights in a list
- ⏱️ Capture green light duration with millisecond precision
- 📊 View captured schedules for each traffic light
- 🗑️ Delete traffic lights and schedules
- 🌙 Dark theme, mobile-optimized design

## Quick Start

### Prerequisites
- Python 3.14+
- Node.js 18+

### Setup

**Backend:**
```bash
poetry install  # or: pip install -r requirements.txt
python main.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` - API docs at `http://localhost:8000/docs`

## Usage

1. Add a traffic light (location, coordinates, notes)
2. Click a light to view details
3. Click "Schedule Information" to capture green light durations
4. Press "Capture Schedule" → "Start" when green turns on → "Stop" when it turns off
5. View all captured schedules with durations

## Database

Uses DuckDB (auto-created on first run as `traffic_lights.duckdb`)

## Tech Stack

- **Backend:** FastAPI, DuckDB, Python 3.14
- **Frontend:** Vue.js 3, Vue Router, Vite