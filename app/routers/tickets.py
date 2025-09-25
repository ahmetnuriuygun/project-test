from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from ..core.database import get_db
from ..schemas.schemas import Ticket, TicketCreate, TicketUpdate, Comment, CommentCreate, DetailedTicket
from ..models.models import Ticket as TicketModel, Comment as CommentModel, User, Student
from ..core.security import get_current_user, get_current_active_user
from ..core.database import get_db
from ..schemas.schemas import Ticket, TicketCreate, TicketUpdate, Comment, CommentCreate, DetailedTicket
from ..models.models import Ticket as TicketModel, Comment as CommentModel, User, Student
from ..core.security import get_current_user, get_current_active_user

router = APIRouter()

@router.post("/tickets/", response_model=Ticket)
def create_ticket(ticket: TicketCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    db_ticket = TicketModel(**ticket.dict(), created_by=current_user.id)
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

@router.get("/tickets/", response_model=List[DetailedTicket])
def list_tickets(
    status: Optional[str] = Query(None),
    assigned_student: Optional[UUID] = Query(None),
    created_by: Optional[UUID] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = db.query(TicketModel)

    if status:
        query = query.filter(TicketModel.status == status)
    if assigned_student:
        query = query.filter(TicketModel.assigned_student == assigned_student)
    if created_by:
        query = query.filter(TicketModel.created_by == created_by)
    if start_date and end_date:
        query = query.filter(TicketModel.created_at.between(start_date, end_date))
    
    tickets = query.offset(skip).limit(limit).all()
    
    # Enhance tickets with user and student details
    for ticket in tickets:
        # Get the creator user
        creator = db.query(User).filter(User.id == ticket.created_by).first()
        if creator:
            ticket.created_by = creator

        # Get the assigned student if exists
        if ticket.assigned_student:
            student = db.query(Student).filter(Student.id == ticket.assigned_student).first()
            if student:
                ticket.assigned_student_details = student
    
    return tickets

@router.get("/tickets/{ticket_id}/", response_model=DetailedTicket)
def get_ticket(ticket_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    ticket = db.query(TicketModel).filter(TicketModel.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Get the creator user
    creator = db.query(User).filter(User.id == ticket.created_by).first()
    if creator:
        ticket.created_by = creator

    # Get the assigned student if exists
    if ticket.assigned_student:
        student = db.query(Student).filter(Student.id == ticket.assigned_student).first()
        if student:
            ticket.assigned_student_details = student

    return ticket

@router.put("/tickets/{ticket_id}/", response_model=Ticket)
def update_ticket(ticket_id: UUID, ticket: TicketUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    db_ticket = db.query(TicketModel).filter(TicketModel.id == ticket_id).first()
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    for key, value in ticket.dict(exclude_unset=True).items():
        setattr(db_ticket, key, value)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

@router.post("/tickets/{ticket_id}/comments/", response_model=Comment)
def add_comment(ticket_id: UUID, comment: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    db_comment = CommentModel(**comment.dict(), author_id=current_user.id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.get("/tickets/{ticket_id}/comments/", response_model=List[Comment])
def list_comments(ticket_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return db.query(CommentModel).filter(CommentModel.ticket_id == ticket_id).all()


@router.get("/students/{student_id}/tickets/", response_model=List[DetailedTicket])
def list_student_tickets(student_id: UUID, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_active_user)):
    tickets = db.query(TicketModel).filter(TicketModel.assigned_student == student_id).all()

    # Enhance tickets with user and student details
    for ticket in tickets:
        # Get the creator user
        creator = db.query(User).filter(User.id == ticket.created_by).first()
        if creator:
            ticket.created_by = creator

        # Get the assigned student if exists
        if ticket.assigned_student:
            student = db.query(Student).filter(Student.id == ticket.assigned_student).first()
            if student:
                ticket.assigned_student_details = student

    return tickets
