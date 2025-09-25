from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import (
    Student, Ticket, User, UserRole, Dormitory, 
    AttendanceSchedule, Attendance, AttendanceStatus,
    Room
)
from app.core.security import get_password_hash
import uuid
from datetime import datetime, timedelta

def create_dummy_data():
    db: Session = next(get_db())
    
    # Create 2 dormitories
    dormitories = []
    dorm_data = [
        {
            "name": "Koninklijk Atheneum Internaat",
            "address": "Kempisch Plein 13, 2300 Turnhout",
            "is_active": True
        },
        {
            "name": "Sint-Victor Internaat",
            "address": "Kasteelplein 20, 2300 Turnhout",
            "is_active": True
        }
    ]

    for dorm in dorm_data:
        dormitory = Dormitory(
            id=uuid.uuid4(),
            **dorm
        )
        db.add(dormitory)
        dormitories.append(dormitory)
    db.commit()

    # Create admin users for each dormitory
    admins = []
    for i, dorm in enumerate(dormitories):
        admin = User(
            id=uuid.uuid4(),
            name=f"Admin {i+1}",
            email=f"admin{i+1}@example.com",
            hashed_password=get_password_hash("password"),
            role=UserRole.ADMIN,
            dormitory_id=dorm.id,
            is_active=True,
            phone=f"+32 49{i} 12 34 56"
        )
        db.add(admin)
        admins.append(admin)
    db.commit()

    # Create staff users for each dormitory
    staff_users = []
    for i, dorm in enumerate(dormitories):
        for j in range(2):  # 2 staff members per dormitory
            staff = User(
                id=uuid.uuid4(),
                name=f"Staff {i+1}-{j+1}",
                email=f"staff{i+1}_{j+1}@example.com",
                hashed_password=get_password_hash("password"),
                role=UserRole.STAFF,
                dormitory_id=dorm.id,
                is_active=True,
                phone=f"+32 48{i} {j}1 23 45"
            )
            db.add(staff)
            staff_users.append(staff)
    db.commit()

    # Create rooms for each dormitory
    rooms = []
    for dorm in dormitories:
        for i in range(5):  # 5 rooms per dormitory
            room = Room(
                id=uuid.uuid4(),
                number=f"{dorm.name[:1]}{100+i}",
                floor=1,
                capacity=2,
                dormitory_id=dorm.id,
                is_active=True
            )
            db.add(room)
            rooms.append(room)
    db.commit()

    # Create students
    students = []
    existing_rfid_tags = set()

    for i, dorm in enumerate(dormitories):
        for j in range(6):  # 6 students per dormitory
            # Generate unique RFID tag
            while True:
                rfid_tag = f"RFID-{uuid.uuid4().hex[:8]}"
                if rfid_tag not in existing_rfid_tags:
                    existing_rfid_tags.add(rfid_tag)
                    break

            # Assign to a room in the same dormitory
            dorm_rooms = [r for r in rooms if r.dormitory_id == dorm.id]
            assigned_room = dorm_rooms[j % len(dorm_rooms)]

            student = Student(
                id=uuid.uuid4(),
                name=f"Student{i+1}-{j+1}",
                surname=f"Lastname{i+1}-{j+1}",
                rfid_tag=rfid_tag,
                date_of_birth=datetime(2005, 1, 1) + timedelta(days=j*100),
                phone=f"+32 46{i} {j}2 34 56",
                email=f"student{i+1}_{j+1}@example.com",
                photo_url="https://picsum.photos/200",
                school="Example High School",
                class_name=f"{10+j}A",
                address=f"Street {j+1}",
                city="Turnhout",
                postal_code="2300",
                school_contact_person="Jane Smith",
                school_contact_email="contact@school.com",
                school_contact_phone="+32 456 78 90 12",
                parent_name=f"Parent {i+1}-{j+1}",
                parent_phone=f"+32 47{i} {j}3 45 67",
                parent_email=f"parent{i+1}_{j+1}@example.com",
                dormitory_id=dorm.id,
                room_id=assigned_room.id,
                is_active=True
            )
            db.add(student)
            students.append(student)
    db.commit()

    # Create attendance schedules for each dormitory
    schedules = []
    for dorm in dormitories:
        # Morning check
        morning = AttendanceSchedule(
            id=uuid.uuid4(),
            name=f"Morning Check - {dorm.name}",
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
            name=f"Evening Check - {dorm.name}",
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

    # Create some attendance records
    for student in students:
        for schedule in [s for s in schedules if s.dormitory_id == student.dormitory_id]:
            # Create a few attendance records for each student
            for day_offset in range(-5, 0):  # Last 5 days
                attendance = Attendance(
                    id=uuid.uuid4(),
                    student_id=student.id,
                    schedule_id=schedule.id,
                    status=AttendanceStatus.PRESENT,
                    timestamp=datetime.now() + timedelta(days=day_offset),
                    recorded_by_id=staff_users[0].id
                )
                db.add(attendance)
    db.commit()

    # Create tickets for each student
    for student in students:
        staff_for_dorm = [s for s in staff_users if s.dormitory_id == student.dormitory_id]
        for i in range(2):  # 2 tickets per student
            ticket = Ticket(
                id=uuid.uuid4(),
                title=f"Issue reported for {student.name}",
                description=f"This is ticket #{i+1} for student {student.name}. It's a sample ticket.",
                status="open",
                created_by=staff_for_dorm[0].id,
                assigned_student=student.id,
                category="General",
                created_at=datetime.now() - timedelta(days=i)
            )
            db.add(ticket)
    db.commit()

    print("Dummy data creation completed successfully:")
    print(f"- Created {len(dormitories)} dormitories")
    print(f"- Created {len(admins)} admin users")
    print(f"- Created {len(staff_users)} staff users")
    print(f"- Created {len(rooms)} rooms")
    print(f"- Created {len(students)} students")
    print(f"- Created {len(schedules)} attendance schedules")
    print("- Created attendance records for the last 5 days")
    print(f"- Created {len(students) * 2} tickets")

if __name__ == "__main__":
    create_dummy_data()
