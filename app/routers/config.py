from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from app.core.database import get_db
from app.models.models import SystemConfig, User, UserRole
from app.schemas.schemas import (
    SystemConfigCreate,
    SystemConfig as SystemConfigSchema
)
from app.routers.auth import get_current_user

router = APIRouter()

async def check_admin_access(current_user: User):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires admin privileges"
        )

@router.post("/config/", response_model=SystemConfigSchema)
async def create_system_config(
    config: SystemConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await check_admin_access(current_user)
    
    existing_config = db.query(SystemConfig).filter(SystemConfig.key == config.key).first()
    if existing_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Configuration with key '{config.key}' already exists"
        )
    
    db_config = SystemConfig(**config.dict())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

@router.get("/config/{key}", response_model=SystemConfigSchema)
async def get_system_config(
    key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return config

@router.put("/config/{key}", response_model=SystemConfigSchema)
async def update_system_config(
    key: str,
    value: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    await check_admin_access(current_user)
    
    config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    config.value = value
    db.commit()
    db.refresh(config)
    return config

@router.get("/config/", response_model=List[SystemConfigSchema])
async def list_system_configs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(SystemConfig).all()
