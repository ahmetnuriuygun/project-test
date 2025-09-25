from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid
from app.core.database import get_db
from app.models.models import AttendanceSchedule, User, UserRole, Dormitory
from app.schemas.schemas import (
    AttendanceScheduleCreate,
    AttendanceScheduleUpdate,
    AttendanceSchedule as AttendanceScheduleSchema
)
from app.routers.auth import get_current_user

router = APIRouter()

async def check_admin_access(current_user: User, dormitory_id: str = None):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires admin privileges"
        )
    
    if dormitory_id and str(current_user.dormitory_id) != dormitory_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only manage schedules for your own dormitory"
        )

@router.post("/attendance-schedules/", response_model=AttendanceScheduleSchema)
async def create_attendance_schedule(
    schedule: AttendanceScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await check_admin_access(current_user, str(schedule.dormitory_id))
    
    # Validate time format
    try:
        datetime.strptime(schedule.start_time, "%H:%M")
        datetime.strptime(schedule.end_time, "%H:%M")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Time must be in HH:MM format"
        )
    
    # Create schedule
    db_schedule = AttendanceSchedule(
        **schedule.dict(),
        created_by_id=current_user.id
    )
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

@router.get("/attendance-schedules/", response_model=List[AttendanceScheduleSchema])
async def list_attendance_schedules(
    dormitory_id: str = None,
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(AttendanceSchedule)
    
    # Filter by dormitory if specified
    if dormitory_id:
        try:
            dormitory_uuid = uuid.UUID(dormitory_id)
            query = query.filter(AttendanceSchedule.dormitory_id == dormitory_uuid)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid dormitory ID format")
    elif current_user.role != UserRole.ADMIN:
        # Non-admin users can only see schedules from their dormitory
        query = query.filter(AttendanceSchedule.dormitory_id == current_user.dormitory_id)
    
    # Filter active schedules if requested
    if active_only:
        query = query.filter(
            AttendanceSchedule.is_active == True,
            AttendanceSchedule.start_date <= datetime.utcnow(),
            (AttendanceSchedule.end_date >= datetime.utcnow()) | (AttendanceSchedule.end_date == None)
        )
    
    return query.all()

@router.get("/attendance-schedules/{schedule_id}", response_model=AttendanceScheduleSchema)
async def get_attendance_schedule(
    schedule_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    schedule = db.query(AttendanceSchedule).filter(AttendanceSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # Check if user has access to this schedule
    if current_user.role != UserRole.ADMIN and current_user.dormitory_id != schedule.dormitory_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this schedule"
        )
    
    return schedule

@router.put("/attendance-schedules/{schedule_id}", response_model=AttendanceScheduleSchema)
async def update_attendance_schedule(
    schedule_id: str,
    schedule_update: AttendanceScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_schedule = db.query(AttendanceSchedule).filter(AttendanceSchedule.id == schedule_id).first()
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    await check_admin_access(current_user, str(db_schedule.dormitory_id))
    
    # Validate time format if provided
    if schedule_update.start_time:
        try:
            datetime.strptime(schedule_update.start_time, "%H:%M")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start time must be in HH:MM format"
            )
    
    if schedule_update.end_time:
        try:
            datetime.strptime(schedule_update.end_time, "%H:%M")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End time must be in HH:MM format"
            )
    
    # Update schedule
    update_data = schedule_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_schedule, field, value)
    
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

@router.delete("/attendance-schedules/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attendance_schedule(
    schedule_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_schedule = db.query(AttendanceSchedule).filter(AttendanceSchedule.id == schedule_id).first()
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    await check_admin_access(current_user, str(db_schedule.dormitory_id))
    
    # Instead of deleting, mark as inactive
    db_schedule.is_active = False
    db.commit()
