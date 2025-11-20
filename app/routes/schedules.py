"""Schedule endpoints including pattern detection."""

from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime, timedelta
from statistics import mean, stdev

from app.models import Schedule, ScheduleCreate, SchedulePattern
from app.database import get_connection, get_next_id

router = APIRouter(
    prefix="/api",
    tags=["Schedules"]
)


@router.get("/traffic-lights/{traffic_light_id}/schedules", response_model=List[Schedule])
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


@router.post("/traffic-lights/{traffic_light_id}/schedules", response_model=Schedule)
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


@router.get("/traffic-lights/{traffic_light_id}/pattern", response_model=SchedulePattern)
def get_schedule_pattern(traffic_light_id: str):
    """Analyze captured schedules and determine traffic light pattern"""
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
        
        total_captures = len(durations)
        last_capture = str(green_ends[-1]) if green_ends else None
        
        # Calculate statistics for duration
        avg_duration = int(mean(durations))
        min_duration = min(durations)
        max_duration = max(durations)
        
        # Calculate cycle time (time between green phase starts)
        cycle_times = []
        if len(green_starts) >= 2:
            for i in range(len(green_starts) - 1):
                cycle_ms = int((green_starts[i + 1] - green_starts[i]).total_seconds() * 1000)
                cycle_times.append(cycle_ms)
        
        avg_cycle_ms = None
        if cycle_times:
            avg_cycle_ms = int(mean(cycle_times))
        
        # Determine regularity
        if total_captures >= 3:
            std_dev = stdev(durations)
            # If standard deviation is less than 10% of mean, it's regular
            regularity_threshold = avg_duration * 0.1
            
            if std_dev < regularity_threshold:
                schedule_regularity = "regular"
            elif std_dev < regularity_threshold * 2:
                schedule_regularity = "somewhat_regular"
            else:
                schedule_regularity = "irregular"
        else:
            std_dev = None
            schedule_regularity = None
        
        # Predict next green phase
        next_green_start = None
        next_green_end = None
        
        if avg_cycle_ms and len(green_starts) > 0:
            # Calculate time since last green start
            last_green_start = green_starts[-1]
            now = datetime.now(last_green_start.tzinfo)
            
            # Predict next start by adding average cycle time to last start
            from datetime import timedelta
            next_start_dt = last_green_start + timedelta(milliseconds=avg_cycle_ms)
            next_green_start = next_start_dt.isoformat()
            
            # Predict next end based on average duration
            next_end_dt = next_start_dt + timedelta(milliseconds=avg_duration)
            next_green_end = next_end_dt.isoformat()
        
        return SchedulePattern(
            has_pattern=True,
            average_duration_ms=avg_duration,
            min_duration_ms=min_duration,
            max_duration_ms=max_duration,
            stddev_duration_ms=std_dev,
            typical_duration_ms=avg_duration,
            schedule_regularity=schedule_regularity,
            total_captures=total_captures,
            last_capture=last_capture,
            average_cycle_ms=avg_cycle_ms,
            next_green_start=next_green_start,
            next_green_end=next_green_end
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
