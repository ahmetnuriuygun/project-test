from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.config import settings
from app.models.models import Student, Attendance, AttendanceStatus, AttendanceType, User, UserRole, UnknownRFID, Ticket, AttendanceSchedule
from app.schemas.schemas import StudentCreate, Student as StudentSchema, StudentUpdate, StudentWithTickets
from app.routers.auth import get_current_user, get_password_hash
import csv
from io import StringIO
from uuid import UUID

router = APIRouter()

def get_or_create_system_user(db: Session) -> User:
    system_user = db.query(User).filter(User.email == "system@dormitory.com").first()
    if not system_user:
        system_user = User(
            email="system@dormitory.com",
            name="System User",
            hashed_password=get_password_hash("not-accessible")
        )
        db.add(system_user)
        db.commit()
        db.refresh(system_user)
    return system_user

async def check_admin_access(current_user: User):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires admin privileges"
        )

async def check_staff_access(current_user: User):
    if current_user.role not in [UserRole.ADMIN, UserRole.STAFF]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires admin or staff privileges"
        )

@router.post("/students/", response_model=StudentSchema)
async def create_student(student: StudentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    await check_staff_access(current_user)
    
    if not current_user.dormitory_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must be assigned to a dormitory to create students"
        )
    
    # Override dormitory_id with the staff's dormitory for non-admin users
    if current_user.role != UserRole.ADMIN:
        student.dormitory_id = current_user.dormitory_id
    elif not student.dormitory_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dormitory ID is required for admin users"
        )
        
    db_student = Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@router.put("/students/{student_id}", response_model=StudentSchema)
async def update_student(
    student_id: str,
    student_update: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await check_staff_access(current_user)
    
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    # Check if user has access to this student's dormitory
    if current_user.role != UserRole.ADMIN and current_user.dormitory_id != db_student.dormitory_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update students in your dormitory"
        )
    
    # For non-admin users, prevent changing dormitory_id
    if current_user.role != UserRole.ADMIN and "dormitory_id" in student_update.dict(exclude_unset=True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can change a student's dormitory"
        )

    update_data = student_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_student, field, value)

    db.commit()
    db.refresh(db_student)
    return db_student

@router.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
    student_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await check_admin_access(current_user)
    
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Soft delete by setting is_active to False
    db_student.is_active = False
    db.commit()
    return None

@router.get("/students/search/", response_model=List[StudentSchema])
async def search_students(
    query: Optional[str] = None,
    room_id: Optional[str] = None,
    is_active: Optional[bool] = True,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    filters = []
    if is_active is not None:
        filters.append(Student.is_active == is_active)
    if room_id:
        filters.append(Student.room_id == room_id)
    if query:
        filters.append(
            or_(
                Student.name.ilike(f"%{query}%"),
                Student.rfid_tag.ilike(f"%{query}%"),
                Student.phone.ilike(f"%{query}%")
            )
        )
    
    students = db.query(Student).filter(*filters).offset(skip).limit(limit).all()
    return students

@router.post("/students/bulk-import/")
async def bulk_import_students(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await check_admin_access(current_user)
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    content = await file.read()
    csv_content = StringIO(content.decode())
    csv_reader = csv.DictReader(csv_content)
    
    imported_count = 0
    errors = []
    
    for row in csv_reader:
        try:
            # Convert date string to datetime if present
            if 'date_of_birth' in row and row['date_of_birth']:
                row['date_of_birth'] = datetime.strptime(row['date_of_birth'], '%Y-%m-%d')
            
            student = StudentCreate(**row)
            db_student = Student(**student.dict())
            db.add(db_student)
            imported_count += 1
        except Exception as e:
            errors.append(f"Error in row {csv_reader.line_num}: {str(e)}")
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error importing students: {str(e)}")
    
    return {
        "message": f"Successfully imported {imported_count} students",
        "errors": errors if errors else None
    }

@router.get("/students/", response_model=List[StudentSchema])
def list_students(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    query = db.query(Student)
    
    # Non-admin users can only see students from their dormitory
    if current_user.role != UserRole.ADMIN:
        query = query.filter(Student.dormitory_id == current_user.dormitory_id)
    
    students = query.offset(skip).limit(limit).all()
    return students

@router.get("/students/{student_id}", response_model=StudentWithTickets)
def get_student(student_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        student_uuid = UUID(student_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid student ID format")

    student = db.query(Student).filter(Student.id == student_uuid).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Fetch tickets for the student
    tickets = db.query(Ticket).filter(Ticket.assigned_student == student_uuid).all()

    return StudentWithTickets(student=student, tickets=tickets)



@router.get("/rfid/unknown/latest")
async def get_latest_unknown_rfid(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    latest_unknown = db.query(UnknownRFID).order_by(UnknownRFID.last_seen.desc()).first()
    if not latest_unknown:
        raise HTTPException(status_code=404, detail="No unknown RFID tags found")
    
    return {
        "rfid_tag": latest_unknown.rfid_tag,
        "last_seen": latest_unknown.last_seen,
        "first_seen": latest_unknown.created_at
    }
