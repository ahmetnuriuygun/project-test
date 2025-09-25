from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.models import Dormitory, User, UserRole
from app.schemas.schemas import DormitoryCreate, Dormitory as DormitorySchema
from app.routers.auth import get_current_user

router = APIRouter()

async def check_admin_access(current_user: User):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires admin privileges"
        )

@router.post("/dormitories/", response_model=DormitorySchema)
async def create_dormitory(
    dormitory: DormitoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await check_admin_access(current_user)
    
    # Check if admin already has a dormitory assigned
    if current_user.dormitory_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin is already assigned to a dormitory"
        )
    
    # Create dormitory
    db_dormitory = Dormitory(**dormitory.dict())
    db.add(db_dormitory)
    db.flush()  # Flush to get the dormitory ID
    
    # Assign admin to the dormitory
    current_user.dormitory_id = db_dormitory.id
    db.add(current_user)
    
    db.commit()
    db.refresh(db_dormitory)
    return db_dormitory

@router.get("/dormitories/", response_model=List[DormitorySchema])
async def list_dormitories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Dormitory)
    
    # Regular admin can only see their own dormitory
    if current_user.role == UserRole.ADMIN and current_user.dormitory_id:
        query = query.filter(Dormitory.id == current_user.dormitory_id)
    
    dormitories = query.offset(skip).limit(limit).all()
    return dormitories

@router.get("/dormitories/{dormitory_id}", response_model=DormitorySchema)
async def get_dormitory(
    dormitory_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dormitory = db.query(Dormitory).filter(Dormitory.id == dormitory_id).first()
    if not dormitory:
        raise HTTPException(status_code=404, detail="Dormitory not found")
    
    # Regular admin can only access their own dormitory
    if current_user.role == UserRole.ADMIN and current_user.dormitory_id != dormitory.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this dormitory"
        )
    
    return dormitory
