"""Traffic Light Assistant API - Main entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import traffic_lights, schedules

# Initialize FastAPI app
app = FastAPI(
    title="Traffic Light Assistant API",
    description="API for managing traffic lights and capturing schedule patterns",
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

# Include routers
app.include_router(traffic_lights.router)
app.include_router(schedules.router)


@app.get("/", tags=["Root"])
def read_root():
    """Welcome endpoint"""
    return {"message": "Traffic Light Assistant API", "version": "0.1.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

