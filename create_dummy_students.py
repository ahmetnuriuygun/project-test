from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Student, Ticket, User
from app.core.security import get_password_hash
import uuid
from datetime import date

def create_dummy_students():
    db: Session = next(get_db())

    # Fetch existing RFID tags to avoid duplicates
    existing_rfid_tags = {student.rfid_tag for student in db.query(Student.rfid_tag).all()}

    dummy_students = []
    for i in range(1, 6):
        rfid_tag = f"RFID-{i}"
        while rfid_tag in existing_rfid_tags:
            rfid_tag = f"RFID-{uuid.uuid4().hex[:8]}"
        existing_rfid_tags.add(rfid_tag)

        dummy_students.append({
            "id": uuid.uuid4(),
            "name": f"Student{i}",
            "surname": f"Surname{i}",
            "rfid_tag": rfid_tag,
            "date_of_birth": date(2005, 1, 1),
            "phone": f"123456789{i}",
            "email": f"student{i}@example.com",
            "photo_url": "https://picsum.photos/200",
            "school": "Example High School",
            "class_name": "10A",
            "address": f"{i} Example Street",
            "city": "Example City",
            "postal_code": "12345",
            "school_contact_person": "Jane Smith",
            "school_contact_email": "jane.smith@example.com",
            "school_contact_phone": "9876543210",
            "parent_name": f"Parent{i}",
            "parent_phone": f"987654321{i}",
            "parent_email": f"parent{i}@example.com",
            "dormitory_id": uuid.uuid4()
        })

    # Create a default user
    default_user = User(
        id=uuid.uuid4(),
        name="Default Staff",
        email="staff@example.com",
        hashed_password=get_password_hash("staff"),
        role="staff",
        is_active=True
    )
    db.add(default_user)
    db.commit()

    # Add tickets for each student
    for student_data in dummy_students:
        student = Student(**student_data)
        db.add(student)
        db.commit()

        for j in range(1, 3):
            ticket = Ticket(
                id=uuid.uuid4(),
                title=f"Ticket {j} for {student.name}",
                description=f"This is ticket {j} for {student.name}",
                status="open",
                created_by=default_user.id,
                assigned_student=student.id,
                category=f"Category {j}",
            )
            db.add(ticket)
    db.commit()

    print("5 dummy students and 2 tickets per student created successfully.")

if __name__ == "__main__":
    create_dummy_students()
