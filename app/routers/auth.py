from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from uuid import UUID
from app.core.database import get_db
from app.core.security import verify_password, create_access_token, verify_token, get_password_hash, blacklist_token, \
    verify_refresh_token, create_refresh_token
from app.models.models import User, UserRole
from app.schemas.schemas import Token, User as UserSchema, UserCreate, UserUpdate, RefreshRequest, RevokeRequest
from app.core.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_token(token, db)
    if not token_data:
        raise credentials_exception
    user = db.query(User).filter(User.email == token_data.email).first()
    if not user:
        raise credentials_exception
    return user


async def get_current_io_device(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role != UserRole.IO_DEVICE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only IO devices can perform this operation"
        )
    return current_user


async def check_admin_access(current_user: User):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires admin privileges"
        )


@router.post("/register", response_model=UserSchema)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user with this email already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new admin user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        name=user.name,
        hashed_password=hashed_password,
        role=UserRole.ADMIN  # Force admin role for registrations
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": user.email})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout")
async def logout(
        body: RevokeRequest,
        current_user: User = Depends(get_current_user),
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    blacklist_token(token, db)
    blacklist_token(body.refresh_token, db)
    return {"message": "Successfully logged out"}


@router.put("/users/me", response_model=UserSchema)
async def update_current_user(
        user_update: UserUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    update_data = user_update.dict(exclude_unset=True)

    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/users/", response_model=List[UserSchema])
async def list_users(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    await check_admin_access(current_user)
    query = db.query(User)
    
    # Admin can only see users from their dormitory
    if current_user.dormitory_id:
        query = query.filter(User.dormitory_id == current_user.dormitory_id)
    
    users = query.offset(skip).limit(limit).all()
    return users


@router.put("/users/{user_id}/role", response_model=UserSchema)
async def update_user_role(
        user_id: str,
        role: UserRole,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    await check_admin_access(current_user)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = role
    db.commit()
    db.refresh(user)
    return user


@router.put("/users/{user_id}/activate", response_model=UserSchema)
async def toggle_user_status(
        user_id: str,
        is_active: bool,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    await check_admin_access(current_user)

    if user_id == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user


@router.post("/refresh-token", response_model=Token)
async def refresh_token(req: RefreshRequest, db: Session = Depends(get_db)):
    """Endpoint to refresh the access token using a valid refresh token."""
    payload = verify_refresh_token(req.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.email == payload["sub"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    blacklist_token(req.refresh_token, db)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token({"sub": user.email})

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/users/dormitory-staff", response_model=UserSchema)
async def create_dormitory_staff(
    user: UserCreate,
    dormitory_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if creator is admin
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create staff users"
        )
    
    # Check if admin has access to this dormitory
    if current_user.dormitory_id != dormitory_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create staff for your dormitory"
        )
    
    # Check if user with this email already exists
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new staff user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        name=user.name,
        hashed_password=hashed_password,
        role=UserRole.STAFF,  # Force staff role
        dormitory_id=dormitory_id  # Assign to dormitory
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/users/{user_id}", response_model=UserSchema)
async def get_user_by_id(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    # Find the user
    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check permissions:
    # - Admins can view any user in their dormitory
    # - Staff can only view themselves and other staff/users in their dormitory
    # - Non-staff users can only view themselves
    if current_user.role == UserRole.ADMIN:
        if current_user.dormitory_id and user.dormitory_id != current_user.dormitory_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view users in your dormitory"
            )
    elif current_user.role == UserRole.STAFF:
        if user.dormitory_id != current_user.dormitory_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view users in your dormitory"
            )
    else:
        if str(current_user.id) != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own profile"
            )

    return user
