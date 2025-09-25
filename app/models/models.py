from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Enum, UUID, Boolean, Integer, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid, enum
import uuid
import enum
from ..core.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    STAFF = "staff"
    SUPERVISOR = "supervisor"
    IO_DEVICE = "io-device"

class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"

class AttendanceType(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"

class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STAFF)
    phone = Column(String)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    dormitory_id = Column(UUID(as_uuid=True), ForeignKey("dormitories.id"))
    photo_url = Column(String, default="https://picsum.photos/200")

    dormitory = relationship("Dormitory", back_populates="users")
    attendances_recorded = relationship("Attendance", back_populates="recorded_by")
    tickets_created = relationship("Ticket", back_populates="creator", foreign_keys="[Ticket.created_by]")
    comments = relationship("Comment", back_populates="author", foreign_keys="[Comment.author_id]")
    rfid_scans = relationship("RFIDLog", back_populates="device")
    assigned_schedules = relationship("AttendanceSchedule",
                                    secondary="attendance_schedule_devices",
                                    back_populates="assigned_devices")

class Room(Base):
    __tablename__ = "rooms"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    number = Column(String, unique=True, nullable=False)
    floor = Column(Integer)
    capacity = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    dormitory_id = Column(UUID(as_uuid=True), ForeignKey("dormitories.id"), nullable=False)
    
    dormitory = relationship("Dormitory", back_populates="rooms")
    students = relationship("Student", back_populates="room")

class Student(Base):
    __tablename__ = "students"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    surname = Column(String)
    rfid_tag = Column(String, unique=True, nullable=False)
    date_of_birth = Column(DateTime)
    enrollment_date = Column(DateTime(timezone=True), server_default=func.now())
    phone = Column(String)
    emergency_contact = Column(String)
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    school = Column(String)
    class_name = Column(String)  # Renamed from 'class' to avoid conflict with Python keyword
    address = Column(String)
    city = Column(String)
    postal_code = Column(String)
    email = Column(String)
    school_contact_person = Column(String)
    school_contact_email = Column(String)
    school_contact_phone = Column(String)
    parent_name = Column(String)
    parent_phone = Column(String)
    parent_email = Column(String)
    photo_url = Column(String, default="https://picsum.photos/200")
    dormitory_id = Column(UUID(as_uuid=True), ForeignKey("dormitories.id"), nullable=False)

    # Relationships
    dormitory = relationship("Dormitory", back_populates="students")
    attendances = relationship("Attendance", back_populates="student")
    room = relationship("Room", back_populates="students")
    tickets_assigned = relationship("Ticket", back_populates="assignee", foreign_keys="[Ticket.assigned_student]")
    rfid_logs = relationship("RFIDLog", back_populates="student")

class Attendance(Base):
    __tablename__ = "attendances"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"))
    schedule_id = Column(UUID(as_uuid=True), ForeignKey("attendance_schedules.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Enum(AttendanceStatus))
    recorded_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    notes = Column(String)
    
    student = relationship("Student", back_populates="attendances")
    recorded_by = relationship("User", back_populates="attendances_recorded")
    schedule = relationship("AttendanceSchedule", back_populates="attendances")

class SystemConfig(Base):
    __tablename__ = "system_config"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String, unique=True, nullable=False)
    value = Column(JSON)
    description = Column(String)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token = Column(String, unique=True, nullable=False)
    blacklisted_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)

class UnknownRFID(Base):
    __tablename__ = "unknown_rfids"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rfid_tag = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True), server_default=func.now())

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assigned_student = Column(UUID(as_uuid=True), ForeignKey("students.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    category = Column(String)

    creator = relationship("User", back_populates="tickets_created")
    assignee = relationship("Student", back_populates="tickets_assigned")
    comments = relationship("Comment", back_populates="ticket")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    ticket = relationship("Ticket", back_populates="comments")
    author = relationship("User", back_populates="comments")

class Dormitory(Base):
    __tablename__ = "dormitories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    address = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    users = relationship("User", back_populates="dormitory")
    attendance_schedules = relationship("AttendanceSchedule", back_populates="dormitory")
    rooms = relationship("Room", back_populates="dormitory")
    students = relationship("Student", back_populates="dormitory")

class AttendanceSchedule(Base):
    __tablename__ = "attendance_schedules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String)
    dormitory_id = Column(UUID(as_uuid=True), ForeignKey("dormitories.id"), nullable=False)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Schedule configuration
    monday = Column(Boolean, default=False)
    tuesday = Column(Boolean, default=False)
    wednesday = Column(Boolean, default=False)
    thursday = Column(Boolean, default=False)
    friday = Column(Boolean, default=False)
    saturday = Column(Boolean, default=False)
    sunday = Column(Boolean, default=False)
    
    # Time configuration
    start_time = Column(String, nullable=False)  # Format: "HH:MM"
    end_time = Column(String, nullable=False)    # Format: "HH:MM"
    
    # Date range
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True))  # Null means indefinite
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_attendance_taken = Column(DateTime(timezone=True))

    # Relationships
    dormitory = relationship("Dormitory", back_populates="attendance_schedules")
    created_by = relationship("User", foreign_keys=[created_by_id])
    attendances = relationship("Attendance", back_populates="schedule")
    assigned_devices = relationship("User", 
                                  secondary="attendance_schedule_devices",
                                  back_populates="assigned_schedules")
    rfid_logs = relationship("RFIDLog", back_populates="attendance_schedule")

# Association table for AttendanceSchedule-Device many-to-many relationship
attendance_schedule_devices = Table(
    'attendance_schedule_devices', Base.metadata,
    Column('schedule_id', UUID(as_uuid=True), ForeignKey('attendance_schedules.id'), primary_key=True),
    Column('device_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True)
)

class RFIDLog(Base):
    __tablename__ = "rfid_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False)
    device_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)  # References IO_DEVICE user
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    attendance_schedule_id = Column(UUID(as_uuid=True), ForeignKey("attendance_schedules.id"), nullable=False)
    
    # Relationships
    student = relationship("Student", back_populates="rfid_logs")
    device = relationship("User", back_populates="rfid_scans")
    attendance_schedule = relationship("AttendanceSchedule", back_populates="rfid_logs")
