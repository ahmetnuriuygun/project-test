from sqlalchemy.orm import Session
from app.core.database import get_db, Base, engine
from app.models.models import (
    Dormitory, User, UserRole, Room, Student,
    AttendanceSchedule, Attendance, AttendanceStatus,
    Ticket, TicketStatus
)
from app.core.security import get_password_hash

# Drop all tables
Base.metadata.drop_all(bind=engine)

# Create database tables
Base.metadata.create_all(bind=engine)
import uuid
from datetime import datetime, timedelta
from typing import List

def create_test_data():
    # Get database session
    db = next(get_db())
    
    print("Starting test data creation...")
    
    # Create dormitories
    dormitories = []
    dorm_data = [
        {
            "name": "Sint-Victor Internaat",
            "address": "Kasteelplein 20, 2300 Turnhout"
        },
        {
            "name": "Sint-Jan Internaat",
            "address": "Collegestraat 27, 2300 Turnhout"
        }
    ]
    
    for dorm in dorm_data:
        db_dorm = Dormitory(
            id=uuid.uuid4(),
            name=dorm["name"],
            address=dorm["address"],
            is_active=True
        )
        db.add(db_dorm)
        dormitories.append(db_dorm)
    db.commit()
    
    print(f"Created {len(dormitories)} dormitories")
    
    # Create admin users for each dormitory
    admins = []
    for i, dorm in enumerate(dormitories):
        admin = User(
            id=uuid.uuid4(),
            name=f"Admin {i+1}",
            email=f"admin{i+1}@internaat.be",
            hashed_password=get_password_hash("password"),
            role=UserRole.ADMIN,
            phone=f"+32 456 78 90 {i+1}",
            is_active=True,
            dormitory_id=dorm.id,
            photo_url="https://picsum.photos/200",

        )
        db.add(admin)
        admins.append(admin)
    db.commit()
    
    print(f"Created {len(admins)} admin users")
    
    # Create staff users for each dormitory
    staff_users = []
    for i, dorm in enumerate(dormitories):
        # Create 3 staff members per dormitory
        for j in range(3):
            staff = User(
                id=uuid.uuid4(),
                name=f"Staff {i+1}-{j+1}",
                email=f"staff{i+1}_{j+1}@internaat.be",
                hashed_password=get_password_hash("password"),
                role=UserRole.STAFF,
                phone=f"+32 456 78 9{i} {j+1}",
                is_active=True,
                dormitory_id=dorm.id,
                photo_url="https://picsum.photos/200",

            )
            db.add(staff)
            staff_users.append(staff)
    db.commit()
    
    print(f"Created {len(staff_users)} staff users")
      # Create rooms for each dormitory
    rooms = []
    for idx, dorm in enumerate(dormitories):
        # Create 5 rooms per dormitory
        for i in range(5):
            floor = i // 2 + 1
            room = Room(
                id=uuid.uuid4(),
                number=f"DORM{idx+1}-{floor}0{i%2 + 1}",  # DORM1-101, DORM1-102, DORM2-101, etc.
                floor=floor,
                capacity=2,
                is_active=True,
                dormitory_id=dorm.id
            )
            db.add(room)
            rooms.append(room)
    db.commit()
    
    print(f"Created {len(rooms)} rooms")
    
    # Create students
    students = []
    schools = ["Sint-Victor College", "Sint-Jan College", "Sint-Jozef College"]
    for i, dorm in enumerate(dormitories):
        # Create 6 students per dormitory
        dorm_rooms = [r for r in rooms if r.dormitory_id == dorm.id]
        for j in range(6):
            rfid_tag = f"RFID{i+1}-{j+1}"
            assigned_room = dorm_rooms[j // 2]  # 2 students per room
            
            student = Student(
                id=uuid.uuid4(),
                name=f"Student{i+1}-{j+1}",
                surname=f"Lastname{i+1}-{j+1}",
                rfid_tag=rfid_tag,
                date_of_birth=datetime(2005, 1, 1) + timedelta(days=j*100),
                phone=f"+32 46{i} {j}2 34 56",
                emergency_contact=f"+32 47{i} {j}2 34 56",
                email=f"student{i+1}_{j+1}@example.com",
                school=schools[j % len(schools)],
                class_name=f"{10+j//2}A",
                address=f"Street {j+1}",
                city="Turnhout",
                postal_code="2300",
                school_contact_person=f"Teacher {j+1}",
                school_contact_email=f"teacher{j+1}@school.be",
                school_contact_phone=f"+32 456 78 90 {j+1}",
                parent_name=f"Parent {i+1}-{j+1}",
                parent_phone=f"+32 47{i} {j}3 45 67",
                parent_email=f"parent{i+1}_{j+1}@example.com",
                photo_url="https://picsum.photos/200",
                dormitory_id=dorm.id,
                room_id=assigned_room.id,
                is_active=True
            )
            db.add(student)
            students.append(student)
    db.commit()
    
    print(f"Created {len(students)} students")
    
    # Create attendance schedules for each dormitory
    schedules = []
    for dorm in dormitories:
        # Morning check
        morning = AttendanceSchedule(
            id=uuid.uuid4(),
            name=f"Morning Check",
            description="Morning attendance check",
            dormitory_id=dorm.id,
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            start_time="07:00",
            end_time="08:30",
            start_date=datetime.now(),
            is_active=True,
            created_by_id=admins[0].id
        )
        db.add(morning)
        schedules.append(morning)
        
        # Evening check
        evening = AttendanceSchedule(
            id=uuid.uuid4(),
            name=f"Evening Check",
            description="Evening attendance check",
            dormitory_id=dorm.id,
            monday=True,
            tuesday=True,
            wednesday=True,
            thursday=True,
            friday=True,
            start_time="21:00",
            end_time="22:30",
            start_date=datetime.now(),
            is_active=True,
            created_by_id=admins[0].id
        )
        db.add(evening)
        schedules.append(evening)
    db.commit()
    
    print(f"Created {len(schedules)} attendance schedules")
    
    # Create attendance records for the last 5 days
    # print("Creating attendance records for the last 5 days...")
    # for student in students:
    #     student_schedules = [s for s in schedules if s.dormitory_id == student.dormitory_id]
    #     for schedule in student_schedules:
    #         # Create attendance records for last 5 days
    #         for day_offset in range(-5, 0):
    #             attendance = Attendance(
    #                 id=uuid.uuid4(),
    #                 student_id=student.id,
    #                 schedule_id=schedule.id,
    #                 status=AttendanceStatus.PRESENT,
    #                 timestamp=datetime(2025, 5, 8) + timedelta(days=day_offset),  # Based on current date May 8, 2025
    #                 recorded_by_id=staff_users[0].id
    #             )
    #             db.add(attendance)
    # db.commit()
    
    # Create tickets for each student
    print("Creating tickets for students...")
    for student in students:
        staff_for_dorm = [s for s in staff_users if s.dormitory_id == student.dormitory_id]
        for i in range(2):  # 2 tickets per student
            ticket = Ticket(
                id=uuid.uuid4(),
                title=f"Issue Report",
                description=f"This is test ticket #{i+1} for student {student.name}. It describes a sample issue that needs attention.",
                status=TicketStatus.OPEN if i == 0 else TicketStatus.IN_PROGRESS,
                created_by=staff_for_dorm[0].id,
                assigned_student=student.id,
                created_at=datetime(2025, 5, 8) - timedelta(days=i)  # Based on current date May 8, 2025
            )
            db.add(ticket)
    db.commit()

    print("\nTest data creation completed successfully:")
    print(f"- Created {len(dormitories)} dormitories")
    print(f"- Created {len(admins)} admin users")
    print(f"- Created {len(staff_users)} staff users")
    print(f"- Created {len(rooms)} rooms")
    print(f"- Created {len(students)} students")
    print(f"- Created {len(schedules)} attendance schedules")
    # print("- Created attendance records for the last 5 days")
    print(f"- Created {len(students) * 2} tickets")

if __name__ == "__main__":
    create_test_data()
