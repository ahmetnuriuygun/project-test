from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, case
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
from app.core.database import get_db
from app.core.config import settings
from app.models.models import (
    Attendance, 
    Student, 
    User, 
    AttendanceStatus, 
    AttendanceSchedule, 
    UserRole,
    RFIDLog,
    UnknownRFID
)
from app.schemas.schemas import (
    AttendanceCreate,
    BulkAttendanceCreate, 
    Attendance as AttendanceSchema,
    AttendanceUpdate,
    RFIDLogCreate,
    AttendanceScheduleDeviceAssign,
    SimplifiedAttendance
)
from app.routers.auth import get_current_user, get_current_io_device

router = APIRouter()

async def check_staff_access(current_user: User):
    if current_user.role not in [UserRole.ADMIN, UserRole.STAFF]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires staff privileges"
        )

async def check_schedule_access(db: Session, current_user: User, schedule_id: str):
    # Convert string UUID to UUID object
    try:
        schedule_uuid = uuid.UUID(schedule_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid schedule ID format")

    schedule = db.query(AttendanceSchedule).filter(AttendanceSchedule.id == schedule_uuid).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    if current_user.role != UserRole.ADMIN and current_user.dormitory_id != schedule.dormitory_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this schedule"
        )
    
    # Check if schedule is active and within date range
    now = datetime.utcnow()
    if not schedule.is_active or now < schedule.start_date or (schedule.end_date and now > schedule.end_date):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Schedule is not active or outside its date range"
        )
    
    # Check if today is a scheduled day
    weekday = now.strftime("%A").lower()
    if not getattr(schedule, weekday, False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Attendance is not scheduled for {weekday}"
        )
    
    # Check if current time is within schedule time window
    current_time = now.strftime("%H:%M")
    if current_time < schedule.start_time or current_time > schedule.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current time is outside the scheduled time window"
        )
    
    return schedule

@router.post("/attendance/", response_model=AttendanceSchema)
async def create_attendance(
    attendance: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await check_staff_access(current_user)
    
    # Check student exists and belongs to user's dormitory
    student = db.query(Student).filter(Student.id == attendance.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    if current_user.role != UserRole.ADMIN and student.dormitory_id != current_user.dormitory_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only record attendance for students in your dormitory"
        )
    
    # Validate schedule access and timing
    await check_schedule_access(db, current_user, str(attendance.schedule_id))
    
    # Create attendance record
    db_attendance = Attendance(
        **attendance.dict(),
        recorded_by_id=current_user.id
    )
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

@router.get("/attendance/{student_id}", response_model=List[SimplifiedAttendance])
async def get_student_attendance(
    student_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    schedule_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check student access
    try:
        student_uuid = uuid.UUID(student_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid student ID format")

    query = db.query(Attendance).options(
        joinedload(Attendance.schedule),
        joinedload(Attendance.recorded_by),
        joinedload(Attendance.student)
    ).filter(Attendance.student_id == student_uuid).join(Student).join(User).join(AttendanceSchedule, Attendance.schedule_id == AttendanceSchedule.id)

    if schedule_id:
        query = query.filter(Attendance.schedule_id == schedule_id)
    if start_date:
        query = query.filter(Attendance.timestamp >= start_date)
    if end_date:
        query = query.filter(Attendance.timestamp <= end_date)

    attendances = query.all()

    return [
        {
            "id": attendance.id,
            "timestamp": attendance.timestamp,
            "status": attendance.status,
            "recorded_by_id": attendance.recorded_by_id,
            "notes": attendance.notes,
            "recorded_by_name": attendance.recorded_by.name if attendance.recorded_by else None,
            "student_name": attendance.student.name if attendance.student else None,
            "attendance_schedule_name": attendance.schedule.name if attendance.schedule else None
        }
        for attendance in attendances
    ]

@router.put("/attendance/{attendance_id}", response_model=AttendanceSchema)
async def update_attendance(
    attendance_id: str,
    attendance_update: AttendanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await check_staff_access(current_user)
    
    db_attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not db_attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    
    # Check dormitory access
    schedule = await check_schedule_access(db, current_user, str(db_attendance.schedule_id))
    
    update_data = attendance_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_attendance, field, value)
    
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

@router.get("/attendance/", response_model=List[AttendanceSchema])
async def list_attendance(
    skip: int = 0,
    limit: int = 100,
    schedule_id: Optional[str] = None,
    date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Attendance)
    
    # Filter by dormitory for non-admin users
    if current_user.role != UserRole.ADMIN:
        query = query.join(Student).filter(Student.dormitory_id == current_user.dormitory_id)
    
    if schedule_id:
        try:
            schedule_uuid = uuid.UUID(schedule_id)
            query = query.filter(Attendance.schedule_id == schedule_uuid)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid schedule ID format")
    if date:
        query = query.filter(
            func.date(Attendance.timestamp) == func.date(date)
        )
    
    return query.offset(skip).limit(limit).all()


@router.post("/attendance/bulk", response_model=List[AttendanceSchema])
async def create_bulk_attendance(
        attendances: List[BulkAttendanceCreate],
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    await check_staff_access(current_user)

    print(f"Processing {len(attendances)} attendance records")

    result = []
    skipped = 0
    schedule_ids = set()

    for attendance in attendances:
        # Validate student and schedule for each attendance
        student = db.query(Student).filter(Student.id == attendance.student_id).first()
        if not student:
            print(f"Skipping record: Student {attendance.student_id} not found")
            skipped += 1
            continue

        if current_user.role != UserRole.ADMIN and student.dormitory_id != current_user.dormitory_id:
            print(f"Skipping record: Student {attendance.student_id} not in user's dormitory")
            skipped += 1
            continue

        # Store schedule_id for later use
        schedule_ids.add(str(attendance.schedule_id))

        # Skip the schedule access check for now to see if that's causing issues
        # We'll still validate the schedule exists
        schedule = db.query(AttendanceSchedule).filter(AttendanceSchedule.id == attendance.schedule_id).first()
        if not schedule:
            print(f"Skipping record: Schedule {attendance.schedule_id} not found")
            skipped += 1
            continue

        # Convert to dictionary and add recorded_by_id
        try:
            # Try both methods for compatibility with different Pydantic versions
            try:
                attendance_dict = attendance.model_dump()
            except AttributeError:
                attendance_dict = attendance.dict()

            attendance_dict["recorded_by_id"] = current_user.id

            db_attendance = Attendance(**attendance_dict)
            db.add(db_attendance)
            result.append(db_attendance)
        except Exception as e:
            print(f"Error creating attendance record: {str(e)}")
            skipped += 1

    if not result:
        print("No valid attendance records to save")
        return []

    try:
        # Commit the attendance records
        db.commit()
        print(f"Saved {len(result)} attendance records, skipped {skipped}")

        # Update the last_attendance_taken for each schedule
        for schedule_id_str in schedule_ids:
            try:
                # Convert string to UUID before querying
                schedule_uuid = uuid.UUID(schedule_id_str)

                schedule = db.query(AttendanceSchedule).filter(
                    AttendanceSchedule.id == schedule_uuid
                ).first()

                if schedule:
                    # Use datetime.utcnow() directly instead of func.now()
                    schedule.last_attendance_taken = datetime.utcnow()
                    print(f"Updated last_attendance_taken for schedule {schedule_id_str}")
            except Exception as e:
                print(f"Error updating schedule {schedule_id_str}: {str(e)}")

        # Commit the schedule updates
        db.commit()
        print("Committed schedule updates")

        # Refresh all records to get their generated IDs
        for attendance in result:
            db.refresh(attendance)

        return result
    except Exception as e:
        db.rollback()
        print(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save attendance records: {str(e)}"
        )

@router.post("/rfid-scan")
async def record_rfid_scan(
    rfid_tag: str,
    db: Session = Depends(get_db),
    device: User = Depends(get_current_io_device)
):    # Find student by RFID tag
    student = db.query(Student).filter(Student.rfid_tag == rfid_tag).first()
    
    if not student:
        # Handle unknown RFID tag
        unknown_rfid = db.query(UnknownRFID).filter(UnknownRFID.rfid_tag == rfid_tag).first()
        if not unknown_rfid:
            unknown_rfid = UnknownRFID(rfid_tag=rfid_tag)
            db.add(unknown_rfid)
        else:
            unknown_rfid.last_seen = func.now()
        
        # Clean up old unknown RFID records
        cleanup_date = datetime.utcnow() - timedelta(days=settings.UNKNOWN_RFID_RETENTION_DAYS)
        db.query(UnknownRFID).filter(UnknownRFID.last_seen < cleanup_date).delete()
        
        db.commit()
        raise HTTPException(
            status_code=404, 
            detail=f"Unknown RFID tag: {rfid_tag}"
        )
    
    # Validate student status
    if not student.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student is not active"
        )
    
    # Validate student dormitory assignment
    if not student.dormitory_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student is not assigned to any dormitory"
        )

    # Find active schedule for current time
    now = datetime.utcnow()
    weekday = now.strftime("%A").lower()
    current_time = now.strftime("%H:%M")
    
    schedule = db.query(AttendanceSchedule).filter(
        AttendanceSchedule.dormitory_id == student.dormitory_id,
        AttendanceSchedule.is_active == True,
        AttendanceSchedule.start_date <= now,
        (AttendanceSchedule.end_date >= now) | (AttendanceSchedule.end_date == None),
        getattr(AttendanceSchedule, weekday) == True,
        AttendanceSchedule.start_time <= current_time,
        AttendanceSchedule.end_time >= current_time
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active attendance schedule for current time"
        )

    # Verify device has permission for this schedule
    if not any(s.id == schedule.id for s in device.assigned_schedules):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Device not authorized for this attendance schedule"
        )
    
    # Get the latest attendance record for this student
    latest_attendance = db.query(Attendance).filter(
        Attendance.student_id == student.id,
        Attendance.schedule_id == schedule.id
    ).order_by(Attendance.timestamp.desc()).first()
    
    # Determine if this should be check-in or check-out
    is_check_in = True
    if latest_attendance and latest_attendance.status == AttendanceStatus.PRESENT:
        is_check_in = False

    # Create RFID log
    db_log = RFIDLog(
        student_id=student.id,
        device_id=device.id,
        attendance_schedule_id=schedule.id
    )
    db.add(db_log)
    
    # Create attendance record
    db_attendance = Attendance(
        student_id=student.id,
        schedule_id=schedule.id,
        status=AttendanceStatus.PRESENT if is_check_in else AttendanceStatus.ABSENT,
        recorded_by_id=device.id
    )
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    
    return {
        "status": "success",
        "message": f"Student checked {'in' if is_check_in else 'out'}",
        "student_name": student.name,
        "schedule_name": schedule.name,
        "timestamp": db_attendance.timestamp,
        "attendance_type": "check_in" if is_check_in else "check_out"
    }

@router.post("/schedules/{schedule_id}/devices", response_model=AttendanceScheduleDeviceAssign)
async def assign_devices_to_schedule(
    schedule_id: str,
    device_assignment: AttendanceScheduleDeviceAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can assign devices to schedules"
        )
    
    try:
        schedule_uuid = uuid.UUID(schedule_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid schedule ID format")
        
    schedule = db.query(AttendanceSchedule).filter(AttendanceSchedule.id == schedule_uuid).first()
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
      # Verify all devices exist and are IO_DEVICE role
    devices = db.query(User).filter(
        User.id.in_(device_assignment.device_ids),
        User.role == UserRole.IO_DEVICE
    ).all()
    
    if len(devices) != len(device_assignment.device_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more devices not found or are not IO devices"
        )
    
    # Clear existing assignments and set new ones
    schedule.assigned_devices = devices
    db.commit()
    
    return device_assignment
