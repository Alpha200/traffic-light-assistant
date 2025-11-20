"""Pydantic models for the Traffic Light Assistant API."""

from pydantic import BaseModel, Field
from typing import Optional


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


class SchedulePattern(BaseModel):
    """Detected traffic light schedule pattern"""
    has_pattern: bool
    average_duration_ms: Optional[int] = None
    min_duration_ms: Optional[int] = None
    max_duration_ms: Optional[int] = None
    stddev_duration_ms: Optional[float] = None
    typical_duration_ms: Optional[int] = None
    schedule_regularity: Optional[str] = None  # "regular", "somewhat_regular", "irregular"
    total_captures: int = 0
    last_capture: Optional[str] = None
    average_cycle_ms: Optional[int] = None  # Average time between green phase starts
    next_green_start: Optional[str] = None  # Predicted next green phase start
    next_green_end: Optional[str] = None  # Predicted next green phase end
