"""Schedule endpoints including pattern detection."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime

from app.models import Schedule, ScheduleCreate, SchedulePattern
from app.database import get_connection, get_next_id
from app.auth import get_current_user
from app.services import PatternDetector

router = APIRouter(
    prefix="/api",
    tags=["Schedules"]
)


@router.get("/traffic-lights/{traffic_light_id}/schedules", response_model=List[Schedule])
def get_schedules(traffic_light_id: str, _: Annotated[dict, Depends(get_current_user)]):
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


@router.post("/traffic-lights/{traffic_light_id}/schedules", response_model=Schedule)
def create_schedule(traffic_light_id: str, schedule: ScheduleCreate, _: Annotated[dict, Depends(get_current_user)]):
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


@router.delete("/schedules/{schedule_id}")
def delete_schedule(schedule_id: str, _: Annotated[dict, Depends(get_current_user)]):
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


@router.get("/traffic-lights/{traffic_light_id}/pattern", response_model=SchedulePattern)
def get_schedule_pattern(traffic_light_id: str, _: Annotated[dict, Depends(get_current_user)]):
    """Analyze captured schedules and determine traffic light pattern with daily pattern detection"""
    try:
        conn = get_connection()
        
        # Verify traffic light exists
        existing = conn.execute(
            "SELECT * FROM traffic_lights WHERE id = ?",
            [traffic_light_id]
        ).fetchall()
        
        if not existing:
            conn.close()
            raise HTTPException(status_code=404, detail="Traffic light not found")
        
        # Get all schedules for this traffic light, ordered by green_start (oldest first)
        result = conn.execute(
            "SELECT duration_ms, green_start, green_end FROM schedules WHERE traffic_light_id = ? ORDER BY green_start ASC",
            [traffic_light_id]
        ).fetchall()
        
        conn.close()
        
        if not result:
            return SchedulePattern(
                has_pattern=False,
                total_captures=0
            )
        
        # Extract data
        durations = [row[0] for row in result]
        green_starts = [datetime.fromisoformat(str(row[1]).replace('Z', '+00:00')) for row in result]
        green_ends = [datetime.fromisoformat(str(row[2]).replace('Z', '+00:00')) for row in result]
        
        # Use PatternDetector service to analyze patterns
        detector = PatternDetector(green_starts, durations)
        pattern_data = detector.analyze()
        
        # Add last_capture to the result
        last_capture = str(green_ends[-1]) if green_ends else None
        pattern_data["last_capture"] = last_capture
        
        return SchedulePattern(**pattern_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
