"""Database setup and utilities."""

import duckdb
import uuid
import os

# Use /app/data for Docker volume, fallback to current directory for local development
DB_PATH = os.getenv("DB_PATH", "/app/data/traffic_lights.duckdb")

# Create data directory if it doesn't exist
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Flag to track if tables have been initialized
_tables_initialized = False


def _initialize_tables(conn):
    """Initialize database tables (called once per session)"""
    global _tables_initialized
    
    if _tables_initialized:
        return
    
    try:
        # Create traffic_lights table if it doesn't exist
        conn.execute("""
            CREATE TABLE IF NOT EXISTS traffic_lights (
                id VARCHAR PRIMARY KEY,
                location VARCHAR NOT NULL,
                latitude DOUBLE,
                longitude DOUBLE,
                notes VARCHAR,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create schedules table if it doesn't exist
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schedules (
                id VARCHAR PRIMARY KEY,
                traffic_light_id VARCHAR NOT NULL,
                green_start TIMESTAMP NOT NULL,
                green_end TIMESTAMP NOT NULL,
                duration_ms INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(traffic_light_id) REFERENCES traffic_lights(id)
            )
        """)
        
        _tables_initialized = True
    except Exception as e:
        # If tables already exist, that's fine
        if "already exists" not in str(e):
            _tables_initialized = True


def get_connection():
    """Get a DuckDB connection and ensure the tables exist"""
    conn = duckdb.connect(DB_PATH, read_only=False)
    _initialize_tables(conn)
    return conn


def get_next_id():
    """Generate a new UUID for a traffic light"""
    return str(uuid.uuid4())
