"""Traffic light endpoints."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from typing import List

from app.models import TrafficLight, TrafficLightCreate, TrafficLightUpdate
from app.database import get_connection, get_next_id
from app.auth import get_current_user

router = APIRouter(
    prefix="/api/traffic-lights",
    tags=["Traffic Lights"]
)


@router.get("", response_model=List[TrafficLight])
def get_traffic_lights(_: Annotated[dict, Depends(get_current_user)]):
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


@router.post("", response_model=TrafficLight)
def create_traffic_light(traffic_light: TrafficLightCreate, _: Annotated[dict, Depends(get_current_user)]):
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


@router.get("/{traffic_light_id}", response_model=TrafficLight)
def get_traffic_light(traffic_light_id: str, _: Annotated[dict, Depends(get_current_user)]):
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


@router.put("/{traffic_light_id}", response_model=TrafficLight)
def update_traffic_light(traffic_light_id: str, traffic_light: TrafficLightUpdate, _: Annotated[dict, Depends(get_current_user)]):
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


@router.delete("/{traffic_light_id}")
def delete_traffic_light(traffic_light_id: str, _: Annotated[dict, Depends(get_current_user)]):
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


@router.delete("")
def delete_all_traffic_lights(_: Annotated[dict, Depends(get_current_user)]):
    """Delete all traffic lights"""
    try:
        conn = get_connection()
        conn.execute("DELETE FROM traffic_lights")
        conn.close()
        return {"message": "All traffic lights deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
