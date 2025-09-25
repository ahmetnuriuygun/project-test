# Dormitory Management System Backend

A FastAPI-based backend system for managing dormitory students and attendance using RFID.

## Features

- User Authentication (JWT)
- Student Management
- RFID-based Attendance System
- Attendance Tracking and Reporting

## Prerequisites

- Python 3.8+
- pip (Python package manager)

## Setup

1. Clone the repository
```bash
git clone [your-repository-url]
cd mijninternaat_backend
```

2. Create a virtual environment
```bash
python -m venv venv
```

3. Activate the virtual environment

Windows:
```bash
.\venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

4. Install dependencies
```bash
pip install -r requirements.txt
```

5. Create a `.env` file in the root directory with the following content:
```
DATABASE_URL=sqlite:///./dormitory.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
UNKNOWN_RFID_RETENTION_DAYS=30  # Days to keep unknown RFID records
```

Make sure to replace `your-secret-key-here` with a secure secret key.

## Running the Application

1. Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## Creating an Admin User

To create an admin user for the system, follow these steps:

1. Start the server if it's not running:
```bash
uvicorn app.main:app --reload
```

2. Send a POST request to create a new user (you can use curl, Postman, or the Swagger UI at `/docs`):
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
-H "Content-Type: application/json" \
-d '{
    "email": "admin@example.com",
    "name": "Admin User",
    "password": "your-secure-password",
    "role": "admin"
}'
```

3. Login with the admin credentials:
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
-H "Content-Type: application/form-data" \
-d "username=admin@example.com" \
-d "password=your-secure-password"
```

4. Save the access token from the response. It will be needed for authenticated requests:
```json
{
    "access_token": "eyJ0eXAiOiJ...",
    "token_type": "bearer"
}
```

5. You can verify the admin access by making a request to the `/api/auth/me` endpoint with the token:
```bash
curl -X GET "http://localhost:8000/api/auth/me" \
-H "Authorization: Bearer your-access-token"
```

Note: Make sure to replace `your-secure-password` with a strong password and save it securely.

## API Documentation

Once the server is running, you can access:
- Interactive API documentation: `http://localhost:8000/docs`
- Alternative API documentation: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user (Public)
- `POST /api/auth/login` - User login (Public)
- `POST /api/auth/logout` - User logout (Authenticated)
- `GET /api/auth/me` - Get current user info (Authenticated)
- `PUT /api/auth/users/me` - Update current user profile (Authenticated)
- `GET /api/auth/users/` - List all users (Admin only)
- `PUT /api/auth/users/{user_id}/role` - Update user role (Admin only)
- `PUT /api/auth/users/{user_id}/activate` - Toggle user active status (Admin only)

### Students
- `POST /api/students/` - Create new student (Staff, Admin)
- `GET /api/students/` - List all students (Authenticated)
- `GET /api/students/{student_id}` - Get student details (Authenticated)
- `PUT /api/students/{student_id}` - Update student information (Staff, Admin)
- `DELETE /api/students/{student_id}` - Soft delete student (Admin only)
- `GET /api/students/search/` - Search students by name, RFID tag, or phone (Authenticated)
- `POST /api/students/bulk-import/` - Bulk import students from CSV (Admin only)

### Rooms
- `POST /api/rooms/` - Create new room (Staff, Admin)
- `GET /api/rooms/` - List all rooms (Authenticated)
- `GET /api/rooms/{room_id}` - Get room details (Authenticated)
- `PUT /api/rooms/{room_id}` - Update room information (Staff, Admin)
- `DELETE /api/rooms/{room_id}` - Soft delete room (Staff, Admin)

### Attendance
- `POST /api/attendance/` - Create attendance record (Staff, Admin)
- `GET /api/attendance/{student_id}` - Get student attendance (Authenticated)
- `POST /api/attendance/rfid-scan` - Record RFID scan attendance (IO_DEVICE)
- `POST /api/attendance/schedules/{schedule_id}/devices` - Assign devices to schedule (Admin)

### Attendance Schedules
- `POST /api/attendance-schedules/` - Create attendance schedule (Admin only)
- `GET /api/attendance-schedules/` - List all attendance schedules (Authenticated)
- `GET /api/attendance-schedules/{schedule_id}` - Get schedule details (Authenticated)
- `PUT /api/attendance-schedules/{schedule_id}` - Update schedule (Admin only)
- `DELETE /api/attendance-schedules/{schedule_id}` - Delete schedule (Admin only)

### System Configuration
- `POST /api/config/` - Create system configuration (Admin only)
- `GET /api/config/` - List all system configurations (Authenticated)
- `GET /api/config/{key}` - Get specific configuration (Authenticated)
- `PUT /api/config/{key}` - Update system configuration (Admin only)

### Ticket Endpoints
- `POST /tickets/` - Create a new ticket (Authenticated)
- `GET /tickets/` - List tickets with optional filters (Authenticated)
- `GET /tickets/{ticket_id}/` - Retrieve a specific ticket by ID (Authenticated)
- `PUT /tickets/{ticket_id}/` - Update a ticket's details (Authenticated)
- `POST /tickets/{ticket_id}/comments/` - Add a comment to a ticket (Authenticated)
- `GET /tickets/{ticket_id}/comments/` - List all comments for a specific ticket (Authenticated)
- `GET /students/{student_id}/tickets/` - List all tickets assigned to a specific student (Authenticated)

### Dormitories
- `POST /api/dormitories/` - Create new dormitory (Admin only)
- `GET /api/dormitories/` - List all dormitories (Authenticated)
- `GET /api/dormitories/{dormitory_id}` - Get dormitory details (Authenticated)
- `PUT /api/dormitories/{dormitory_id}` - Update dormitory (Admin only)
- `DELETE /api/dormitories/{dormitory_id}` - Soft delete dormitory (Admin only)

## Permission Levels
- **Public**: No authentication required
- **Authenticated**: Any logged-in user (Admin, Staff, Supervisor, or IO_DEVICE)
- **Staff**: Users with Staff or Admin role
- **Admin**: Users with Admin role only
- **Supervisor**: Users with Supervisor role
- **IO_DEVICE**: RFID devices with IO_DEVICE role

## Data Models

### User
- `id` (UUID) - Primary key
- `name` (String) - User's full name
- `email` (String) - Unique email address
- `hashed_password` (String) - Encrypted password
- `role` (UserRole) - Role enum: ADMIN, STAFF, or SUPERVISOR
- `phone` (String) - Contact number
- `is_active` (Boolean) - Account status
- `last_login` (DateTime) - Last login timestamp
- `created_at` (DateTime) - Account creation timestamp

### Room
- `id` (UUID) - Primary key
- `number` (String) - Unique room number
- `floor` (Integer) - Floor number
- `capacity` (Integer) - Maximum occupancy
- `is_active` (Boolean) - Room status
- `created_at` (DateTime) - Creation timestamp
- `students` (Relationship) - List of students in room

### Student
- `id` (UUID) - Primary key
- `name` (String) - Student's full name
- `surname` (String) - Student's surname
- `rfid_tag` (String) - Unique RFID identifier
- `date_of_birth` (DateTime) - Birth date
- `enrollment_date` (DateTime) - Enrollment timestamp
- `phone` (String) - Contact number
- `emergency_contact` (String) - Emergency contact info
- `room_id` (UUID) - Foreign key to Room
- `is_active` (Boolean) - Student status
- `created_at` (DateTime) - Record creation timestamp
- `school` (String) - School name
- `class_name` (String) - Class/Grade name
- `address` (String) - Home address
- `city` (String) - City of residence
- `postal_code` (String) - Postal code
- `email` (String) - Student email
- `school_contact_person` (String) - School contact person
- `school_contact_email` (String) - School contact email
- `school_contact_phone` (String) - School contact phone
- `parent_name` (String) - Parent/Guardian name
- `parent_phone` (String) - Parent/Guardian phone
- `parent_email` (String) - Parent/Guardian email
- `photo_url` (String) - Student photo URL
- `dormitory_id` (UUID) - Foreign key to Dormitory
- `dormitory` (Relationship) - Associated dormitory
- `attendances` (Relationship) - List of attendance records
- `room` (Relationship) - Associated room
- `tickets_assigned` (Relationship) - Tickets assigned to this student

### Attendance
- `id` (UUID) - Primary key
- `student_id` (UUID) - Foreign key to Student
- `schedule_id` (UUID) - Foreign key to AttendanceSchedule
- `timestamp` (DateTime) - Record timestamp
- `status` (AttendanceStatus) - Status enum: PRESENT, ABSENT, or LATE
- `recorded_by_id` (UUID) - Foreign key to User
- `notes` (String) - Additional notes
- `student` (Relationship) - Associated student
- `recorded_by` (Relationship) - User who recorded attendance
- `schedule` (Relationship) - Associated attendance schedule

### AttendanceRule
- `id` (UUID) - Primary key
- `name` (String) - Rule name
- `check_in_time` (String) - Required check-in time (HH:MM)
- `check_out_time` (String) - Required check-out time (HH:MM)
- `late_threshold` (Integer) - Minutes allowed for late arrival
- `is_active` (Boolean) - Rule status
- `created_at` (DateTime) - Creation timestamp

### SystemConfig
- `id` (UUID) - Primary key
- `key` (String) - Unique configuration key
- `value` (JSON) - Configuration value
- `description` (String) - Configuration description
- `updated_at` (DateTime) - Last update timestamp
- `created_at` (DateTime) - Creation timestamp

### BlacklistedToken
- `id` (UUID) - Primary key
- `token` (String) - Unique JWT token
- `blacklisted_at` (DateTime) - Blacklist timestamp
- `expires_at` (DateTime) - Token expiration timestamp

### Ticket
- `id` (UUID) - Primary key
- `title` (String) - Ticket title
- `description` (String) - Ticket description
- `status` (String) - Ticket status
- `assigned_student` (UUID) - Foreign key to Student
- `created_by` (UUID) - Foreign key to User
- `created_at` (DateTime) - Ticket creation timestamp
- `updated_at` (DateTime) - Last update timestamp
- `comments` (Relationship) - List of comments on the ticket
- `student` (Relationship) - Associated student
- `creator` (Relationship) - User who created the ticket

### Comment
- `id` (UUID) - Primary key
- `ticket_id` (UUID) - Foreign key to Ticket
- `content` (String) - Comment content
- `created_at` (DateTime) - Comment creation timestamp
- `updated_at` (DateTime) - Last update timestamp
- `ticket` (Relationship) - Associated ticket

### RFIDLog
- `id` (UUID) - Primary key
- `student_id` (UUID) - Foreign key to Student
- `device_id` (UUID) - Foreign key to User (IO_DEVICE)
- `timestamp` (DateTime) - Scan timestamp
- `attendance_schedule_id` (UUID) - Foreign key to AttendanceSchedule
- `student` (Relationship) - Associated student
- `device` (Relationship) - Associated RFID device
- `attendance_schedule` (Relationship) - Associated schedule

### AttendanceSchedule
- `id` (UUID) - Primary key
- `name` (String) - Schedule name
- `description` (String) - Schedule description
- `dormitory_id` (UUID) - Foreign key to Dormitory
- `created_by_id` (UUID) - Foreign key to User
- `monday` (Boolean) - Schedule active on Monday
- `tuesday` (Boolean) - Schedule active on Tuesday
- `wednesday` (Boolean) - Schedule active on Wednesday
- `thursday` (Boolean) - Schedule active on Thursday
- `friday` (Boolean) - Schedule active on Friday
- `saturday` (Boolean) - Schedule active on Saturday
- `sunday` (Boolean) - Schedule active on Sunday
- `start_time` (String) - Daily start time (HH:MM)
- `end_time` (String) - Daily end time (HH:MM)
- `start_date` (DateTime) - Schedule start date
- `end_date` (DateTime) - Schedule end date (optional)
- `is_active` (Boolean) - Schedule status
- `created_at` (DateTime) - Creation timestamp
- `updated_at` (DateTime) - Last update timestamp
- `dormitory` (Relationship) - Associated dormitory
- `created_by` (Relationship) - User who created the schedule
- `attendances` (Relationship) - List of attendances for this schedule
- `assigned_devices` (Relationship) - List of RFID devices assigned to this schedule

### Dormitory
- `id` (UUID) - Primary key
- `name` (String) - Dormitory name
- `address` (String) - Physical address
- `created_at` (DateTime) - Creation timestamp
- `is_active` (Boolean) - Dormitory status
- `users` (Relationship) - List of associated users
- `attendance_schedules` (Relationship) - List of attendance schedules
- `rooms` (Relationship) - List of rooms in the dormitory
- `students` (Relationship) - List of students in the dormitory
