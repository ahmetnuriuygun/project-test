from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.models import Room, User, UserRole
from app.schemas.schemas import RoomCreate, Room as RoomSchema
from app.routers.auth import get_current_user

router = APIRouter()

async def check_staff_access(current_user: User):
    if current_user.role not in [UserRole.ADMIN, UserRole.STAFF]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires staff privileges"
        )

@router.post("/rooms/", response_model=RoomSchema)
async def create_room(
    room: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await check_staff_access(current_user)
    
    if not current_user.dormitory_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must be assigned to a dormitory to create rooms"
        )
    
    # Check if room number already exists in this dormitory
    existing_room = db.query(Room).filter(
        Room.number == room.number,
        Room.dormitory_id == current_user.dormitory_id
    ).first()
    if existing_room:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Room with number {room.number} already exists in this dormitory"
        )
    
    db_room = Room(**room.dict(), dormitory_id=current_user.dormitory_id)
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

@router.get("/rooms/", response_model=List[RoomSchema])
async def list_rooms(
    floor: Optional[int] = None,
    is_active: Optional[bool] = True,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Room)
    
    # Filter by floor if specified
    if floor is not None:
        query = query.filter(Room.floor == floor)
    if is_active is not None:
        query = query.filter(Room.is_active == is_active)
        
    # Non-admin users can only see rooms from their dormitory
    if current_user.role != UserRole.ADMIN:
        query = query.filter(Room.dormitory_id == current_user.dormitory_id)
    
    rooms = query.offset(skip).limit(limit).all()
    return rooms

@router.get("/rooms/{room_id}", response_model=RoomSchema)
async def get_room(
    room_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@router.put("/rooms/{room_id}", response_model=RoomSchema)
async def update_room(
    room_id: str,
    room: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await check_staff_access(current_user)
    
    db_room = db.query(Room).filter(Room.id == room_id).first()
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Check if the new room number conflicts with another room
    if room.number != db_room.number:
        existing_room = db.query(Room).filter(Room.number == room.number).first()
        if existing_room:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Room with number {room.number} already exists"
            )
    
    for field, value in room.dict().items():
        setattr(db_room, field, value)
    
    db.commit()
    db.refresh(db_room)
    return db_room

@router.delete("/rooms/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(
    room_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await check_staff_access(current_user)
    
    db_room = db.query(Room).filter(Room.id == room_id).first()
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Soft delete by setting is_active to False
    db_room.is_active = False
    db.commit()
    return None
