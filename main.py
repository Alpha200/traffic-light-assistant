from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import duckdb
from typing import List, Optional
from datetime import datetime
import os
import uuid

# Initialize FastAPI app
app = FastAPI(
    title="Traffic Light Assistant API",
    description="API for managing traffic lights",
    version="0.1.0"
)

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (can be restricted to specific URLs)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DB_PATH = "traffic_lights.duckdb"

def get_connection():
    """Get a DuckDB connection and ensure the table exists"""
    conn = duckdb.connect(DB_PATH)
    
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
    
    return conn

def get_next_id():
    """Generate a new UUID for a traffic light"""
    return str(uuid.uuid4())

# Pydantic models
class TrafficLightCreate(BaseModel):
    location: str = Field(..., description="Location name of the traffic light")
    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")
    notes: Optional[str] = Field(None, description="Additional notes")

class TrafficLightUpdate(BaseModel):
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    notes: Optional[str] = None

class TrafficLight(BaseModel):
    id: str
    location: str
    latitude: Optional[float]
    longitude: Optional[float]
    notes: Optional[str]
    last_updated: str
    created_at: str

# Schedule models
class ScheduleCreate(BaseModel):
    traffic_light_id: str = Field(..., description="Traffic light ID")
    green_start: str = Field(..., description="ISO format timestamp when green light started")
    green_end: str = Field(..., description="ISO format timestamp when green light ended")

class Schedule(BaseModel):
    id: str
    traffic_light_id: str
    green_start: str
    green_end: str
    duration_ms: int
    created_at: str

# API Endpoints

@app.get("/", tags=["Root"])
def read_root():
    """Welcome endpoint"""
    return {"message": "Traffic Light Assistant API", "version": "0.1.0"}

@app.get("/api/traffic-lights", response_model=List[TrafficLight], tags=["Traffic Lights"])
def get_traffic_lights():
    """Get all traffic lights"""
    try:
        conn = get_connection()
        result = conn.execute(
            "SELECT * FROM traffic_lights ORDER BY created_at DESC"
        ).fetchall()
        
        conn.close()
        
        traffic_lights = []
        for row in result:
            traffic_lights.append(TrafficLight(
                id=row[0],
                location=row[1],
                latitude=row[2],
                longitude=row[3],
                notes=row[4],
                last_updated=str(row[5]),
                created_at=str(row[6])
            ))
        
        return traffic_lights
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/traffic-lights", response_model=TrafficLight, tags=["Traffic Lights"])
def create_traffic_light(traffic_light: TrafficLightCreate):
    """Create a new traffic light"""
    try:
        conn = get_connection()
        new_id = get_next_id()
        
        result = conn.execute(
            """
            INSERT INTO traffic_lights (id, location, latitude, longitude, notes)
            VALUES (?, ?, ?, ?, ?)
            RETURNING *
            """,
            [new_id, traffic_light.location, traffic_light.latitude, 
             traffic_light.longitude, traffic_light.notes]
        ).fetchall()
        
        conn.close()
        
        if result:
            row = result[0]
            return TrafficLight(
                id=row[0],
                location=row[1],
                latitude=row[2],
                longitude=row[3],
                notes=row[4],
                last_updated=str(row[5]),
                created_at=str(row[6])
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/traffic-lights/{traffic_light_id}", response_model=TrafficLight, tags=["Traffic Lights"])
def get_traffic_light(traffic_light_id: str):
    """Get a specific traffic light by ID"""
    try:
        conn = get_connection()
        
        result = conn.execute(
            "SELECT * FROM traffic_lights WHERE id = ?",
            [traffic_light_id]
        ).fetchall()
        
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Traffic light not found")
        
        row = result[0]
        return TrafficLight(
            id=row[0],
            location=row[1],
            latitude=row[2],
            longitude=row[3],
            notes=row[4],
            last_updated=str(row[5]),
            created_at=str(row[6])
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/traffic-lights/{traffic_light_id}", response_model=TrafficLight, tags=["Traffic Lights"])
def update_traffic_light(traffic_light_id: str, traffic_light: TrafficLightUpdate):
    """Update a traffic light"""
    try:
        conn = get_connection()
        
        # Check if traffic light exists
        existing = conn.execute(
            "SELECT * FROM traffic_lights WHERE id = ?",
            [traffic_light_id]
        ).fetchall()
        
        if not existing:
            conn.close()
            raise HTTPException(status_code=404, detail="Traffic light not found")
        
        # Build update query dynamically
        update_fields = []
        values = []
        
        if traffic_light.location is not None:
            update_fields.append("location = ?")
            values.append(traffic_light.location)
        
        if traffic_light.latitude is not None:
            update_fields.append("latitude = ?")
            values.append(traffic_light.latitude)
        
        if traffic_light.longitude is not None:
            update_fields.append("longitude = ?")
            values.append(traffic_light.longitude)
        
        if traffic_light.notes is not None:
            update_fields.append("notes = ?")
            values.append(traffic_light.notes)
        
        if update_fields:
            update_fields.append("last_updated = CURRENT_TIMESTAMP")
            values.append(traffic_light_id)
            
            query = f"UPDATE traffic_lights SET {', '.join(update_fields)} WHERE id = ? RETURNING *"
            result = conn.execute(query, values).fetchall()
        else:
            result = conn.execute(
                "SELECT * FROM traffic_lights WHERE id = ?",
                [traffic_light_id]
            ).fetchall()
        
        conn.close()
        
        row = result[0]
        return TrafficLight(
            id=row[0],
            location=row[1],
            latitude=row[2],
            longitude=row[3],
            notes=row[4],
            last_updated=str(row[5]),
            created_at=str(row[6])
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/traffic-lights/{traffic_light_id}", tags=["Traffic Lights"])
def delete_traffic_light(traffic_light_id: str):
    """Delete a traffic light"""
    try:
        conn = get_connection()
        
        # Check if traffic light exists
        existing = conn.execute(
            "SELECT * FROM traffic_lights WHERE id = ?",
            [traffic_light_id]
        ).fetchall()
        
        if not existing:
            conn.close()
            raise HTTPException(status_code=404, detail="Traffic light not found")
        
        conn.execute("DELETE FROM traffic_lights WHERE id = ?", [traffic_light_id])
        conn.close()
        
        return {"message": f"Traffic light {traffic_light_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/traffic-lights", tags=["Traffic Lights"])
def delete_all_traffic_lights():
    """Delete all traffic lights"""
    try:
        conn = get_connection()
        conn.execute("DELETE FROM traffic_lights")
        conn.close()
        return {"message": "All traffic lights deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Schedule Endpoints

@app.get("/api/traffic-lights/{traffic_light_id}/schedules", response_model=List[Schedule], tags=["Schedules"])
def get_schedules(traffic_light_id: str):
    """Get all schedules for a traffic light"""
    try:
        conn = get_connection()
        result = conn.execute(
            "SELECT * FROM schedules WHERE traffic_light_id = ? ORDER BY created_at DESC",
            [traffic_light_id]
        ).fetchall()
        conn.close()
        
        schedules = []
        for row in result:
            schedules.append(Schedule(
                id=row[0],
                traffic_light_id=row[1],
                green_start=str(row[2]),
                green_end=str(row[3]),
                duration_ms=row[4],
                created_at=str(row[5])
            ))
        
        return schedules
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/traffic-lights/{traffic_light_id}/schedules", response_model=Schedule, tags=["Schedules"])
def create_schedule(traffic_light_id: str, schedule: ScheduleCreate):
    """Create a new schedule for a traffic light"""
    try:
        # Verify traffic light exists
        conn = get_connection()
        existing = conn.execute(
            "SELECT * FROM traffic_lights WHERE id = ?",
            [traffic_light_id]
        ).fetchall()
        
        if not existing:
            conn.close()
            raise HTTPException(status_code=404, detail="Traffic light not found")
        
        # Parse timestamps and calculate duration
        from datetime import datetime
        green_start = datetime.fromisoformat(schedule.green_start.replace('Z', '+00:00'))
        green_end = datetime.fromisoformat(schedule.green_end.replace('Z', '+00:00'))
        duration_ms = int((green_end - green_start).total_seconds() * 1000)
        
        new_id = get_next_id()
        
        result = conn.execute(
            """
            INSERT INTO schedules (id, traffic_light_id, green_start, green_end, duration_ms)
            VALUES (?, ?, ?, ?, ?)
            RETURNING *
            """,
            [new_id, traffic_light_id, schedule.green_start, schedule.green_end, duration_ms]
        ).fetchall()
        
        conn.close()
        
        if result:
            row = result[0]
            return Schedule(
                id=row[0],
                traffic_light_id=row[1],
                green_start=str(row[2]),
                green_end=str(row[3]),
                duration_ms=row[4],
                created_at=str(row[5])
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/schedules/{schedule_id}", tags=["Schedules"])
def delete_schedule(schedule_id: str):
    """Delete a schedule"""
    try:
        conn = get_connection()
        
        existing = conn.execute(
            "SELECT * FROM schedules WHERE id = ?",
            [schedule_id]
        ).fetchall()
        
        if not existing:
            conn.close()
            raise HTTPException(status_code=404, detail="Schedule not found")
        
        conn.execute("DELETE FROM schedules WHERE id = ?", [schedule_id])
        conn.close()
        
        return {"message": f"Schedule {schedule_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

