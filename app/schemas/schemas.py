from pydantic import BaseModel, EmailStr, UUID4
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    STAFF = "staff"
    SUPERVISOR = "supervisor"
    IO_DEVICE = "io-device"

class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"

class AttendanceType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"

class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"

class RoomBase(BaseModel):
    number: str
    floor: Optional[int] = None
    capacity: int
    is_active: Optional[bool] = True

class RoomCreate(RoomBase):
    pass

class Room(RoomBase):
    id: UUID4
    created_at: datetime
    dormitory_id: UUID4
    dormitory: Optional["Dormitory"] = None
    
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: Optional[UserRole] = UserRole.STAFF
    phone: Optional[str] = None
    is_active: Optional[bool] = True
    photo_url: Optional[str] = "https://picsum.photos/200"


class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class User(UserBase):
    id: UUID4
    last_login: Optional[datetime] = None
    created_at: datetime
    dormitory_id: Optional[UUID4] = None
    dormitory: Optional["Dormitory"] = None

    class Config:
        from_attributes = True

class StudentBase(BaseModel):
    name: str
    surname: Optional[str] = None
    rfid_tag: str
    date_of_birth: Optional[datetime] = None
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    room_id: Optional[UUID4] = None
    is_active: Optional[bool] = True
    school: Optional[str] = None
    class_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    email: Optional[EmailStr] = None
    school_contact_person: Optional[str] = None
    school_contact_email: Optional[EmailStr] = None
    school_contact_phone: Optional[str] = None
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    parent_email: Optional[EmailStr] = None
    photo_url: Optional[str] = "https://picsum.photos/200"
    dormitory_id: Optional[UUID4] = None
    

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    rfid_tag: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    room_id: Optional[UUID4] = None
    is_active: Optional[bool] = None
    school: Optional[str] = None
    class_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    email: Optional[EmailStr] = None
    school_contact_person: Optional[str] = None
    school_contact_email: Optional[EmailStr] = None
    school_contact_phone: Optional[str] = None
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    parent_email: Optional[EmailStr] = None
    photo_url: Optional[str] = None
    dormitory_id: Optional[UUID4] = None

class Student(StudentBase):
    id: UUID4
    enrollment_date: datetime
    created_at: datetime
    room: Optional[Room] = None
    dormitory: Optional["Dormitory"] = None

    class Config:
        from_attributes = True

class AttendanceBase(BaseModel):
    student_id: UUID4
    schedule_id: UUID4
    status: AttendanceStatus
    notes: Optional[str] = None
    recorded_by_id: UUID4  # Include recorded_by_id in the base schema

class BulkAttendanceCreate(BaseModel):
    student_id: UUID4
    schedule_id: UUID4
    status: AttendanceStatus
    notes: Optional[str] = None

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceUpdate(BaseModel):
    status: Optional[AttendanceStatus] = None
    notes: Optional[str] = None

class Attendance(AttendanceBase):
    id: UUID4
    timestamp: datetime
    recorded_by_id: UUID4
    student: Optional[Student] = None
    recorded_by: Optional[User] = None

    class Config:
        from_attributes = True

class AttendanceRuleBase(BaseModel):
    name: str
    check_in_time: str
    check_out_time: str
    late_threshold: Optional[int] = 15
    is_active: Optional[bool] = True

class AttendanceRuleCreate(AttendanceRuleBase):
    pass

class AttendanceRule(AttendanceRuleBase):
    id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True

class SystemConfigBase(BaseModel):
    key: str
    value: Dict[str, Any]
    description: Optional[str] = None

class SystemConfigCreate(SystemConfigBase):
    pass

class SystemConfig(SystemConfigBase):
    id: UUID4
    updated_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class RefreshRequest(BaseModel):
        refresh_token: str

class RevokeRequest(BaseModel):
    refresh_token: str

class TokenData(BaseModel):
    email: Optional[str] = None

class TicketBase(BaseModel):
    title: str
    description: str
    status: Optional[TicketStatus] = TicketStatus.OPEN
    assigned_student: Optional[UUID4] = None
    category: Optional[str] = None

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TicketStatus] = None
    assigned_student: Optional[UUID4] = None

class UserShort(BaseModel):
    id: UUID4
    name: str
    surname: Optional[str] = None
    photo_url: Optional[str] = None



    class Config:
        from_attributes = True

class StudentShort(BaseModel):
    id: UUID4
    name: str
    surname: str
    photo_url: Optional[str] = None

    class Config:
        from_attributes = True

class DetailedTicket(TicketBase):
    id: UUID4
    created_by: UserShort
    created_at: datetime
    updated_at: Optional[datetime] = None
    assigned_student_details: Optional[StudentShort] = None

    class Config:
        from_attributes = True

class Ticket(TicketBase):
    id: UUID4
    created_by: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None


    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    ticket_id: UUID4

class Comment(CommentBase):
    id: UUID4
    ticket_id: UUID4
    author_id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True

class StudentWithTickets(BaseModel):
    student: Student
    tickets: List[Ticket]

class DormitoryBase(BaseModel):
    name: str
    address: Optional[str] = None
    is_active: Optional[bool] = True

class DormitoryCreate(DormitoryBase):
    pass

class Dormitory(DormitoryBase):
    id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True

class AttendanceScheduleBase(BaseModel):
    name: str
    description: Optional[str] = None
    dormitory_id: UUID4
    monday: Optional[bool] = False
    tuesday: Optional[bool] = False
    wednesday: Optional[bool] = False
    thursday: Optional[bool] = False
    friday: Optional[bool] = False
    saturday: Optional[bool] = False
    sunday: Optional[bool] = False
    start_time: str  # Format: "HH:MM"
    end_time: str    # Format: "HH:MM"
    start_date: datetime
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = True


class AttendanceScheduleCreate(AttendanceScheduleBase):
    pass

class AttendanceScheduleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    monday: Optional[bool] = None
    tuesday: Optional[bool] = None
    wednesday: Optional[bool] = None
    thursday: Optional[bool] = None
    friday: Optional[bool] = None
    saturday: Optional[bool] = None
    sunday: Optional[bool] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None

class AttendanceSchedule(AttendanceScheduleBase):
    id: UUID4
    created_by_id: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_attendance_taken: Optional[datetime] = None  # Make sure this field is included
    dormitory: Optional[Dormitory] = None
    created_by: Optional[User] = None

    class Config:
        from_attributes = True

class RFIDLogBase(BaseModel):
    student_id: UUID4
    device_id: UUID4
    attendance_schedule_id: UUID4

class RFIDLogCreate(RFIDLogBase):
    pass

class RFIDLog(RFIDLogBase):
    id: UUID4
    timestamp: datetime

    class Config:
        from_attributes = True

class UnknownRFIDBase(BaseModel):
    rfid_tag: str

class UnknownRFIDCreate(UnknownRFIDBase):
    pass

class UnknownRFID(UnknownRFIDBase):
    id: UUID4
    created_at: datetime
    last_seen: datetime

    class Config:
        from_attributes = True

class BlacklistedTokenBase(BaseModel):
    token: str
    expires_at: datetime

class BlacklistedTokenCreate(BlacklistedTokenBase):
    pass

class BlacklistedToken(BlacklistedTokenBase):
    id: UUID4
    blacklisted_at: datetime

    class Config:
        from_attributes = True

class AttendanceScheduleDeviceAssign(BaseModel):
    device_ids: list[UUID4]

    class Config:
        from_attributes = True

class SimplifiedAttendance(BaseModel):
    id: UUID4
    timestamp: datetime
    status: AttendanceStatus
    recorded_by_id: UUID4
    notes: Optional[str] = None
    recorded_by_name: Optional[str] = None  # Add the name of the person who recorded it
    student_name: Optional[str] = None  # Add the name of the student
    attendance_schedule_name: Optional[str] = None  # Include the name of the attendance schedule

    class Config:
        from_attributes = True
