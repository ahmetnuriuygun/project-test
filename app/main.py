from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, students, attendance, config, rooms, dormitories, attendance_schedules
from app.core.database import engine
from app.models import models
from app.routers.tickets import router as tickets_router
import logging
from starlette.middleware.base import BaseHTTPMiddleware

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Dormitory Management System",
    description="API for managing dormitory students and attendance using RFID",
    version="1.0.0"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn")

class LogRequestsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        logger.info(f"Incoming request: {request.method} {request.url}")
        logger.info(f"Headers: {dict(request.headers)}")
        response = await call_next(request)
        return response

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add the middleware to log requests
app.add_middleware(LogRequestsMiddleware)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(rooms.router, prefix="/api", tags=["Rooms"])
app.include_router(students.router, prefix="/api", tags=["Students"])
app.include_router(attendance.router, prefix="/api", tags=["Attendance"])
app.include_router(attendance_schedules.router, prefix="/api", tags=["Attendance Schedules"])
app.include_router(dormitories.router, prefix="/api", tags=["Dormitories"])
app.include_router(config.router, prefix="/api", tags=["System Configuration"])
app.include_router(tickets_router, prefix="/api/v1", tags=["Tickets"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Dormitory Management System API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

# Run the application using uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="192.168.0.58", port=8000, reload=True)
