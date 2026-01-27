# app/routers/users.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.user import User, UniversityEnum
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class UserPublic(BaseModel):
    id: int
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    university: Optional[str]
    profile_picture_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("/", response_model=List[UserPublic])
def get_public_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    university: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get a list of public user profiles for the Community page.
    Sensitive data like email and hashed_password are excluded.
    """
    query = db.query(User).filter(User.is_active == True)
    
    if university:
        query = query.filter(User.university == university)
        
    users = query.offset(skip).limit(limit).all()
    
    # Simple conversion for enum to string if needed
    for user in users:
        if user.university:
            user.university = user.university.value if hasattr(user.university, 'value') else str(user.university)
            
    return users
