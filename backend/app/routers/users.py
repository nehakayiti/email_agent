"""
API routes for user management operations.
"""
import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime

from ..db import get_db
from ..models.user import User
from ..dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}}
)

class UserProfile(BaseModel):
    """User profile response model"""
    email: EmailStr
    name: str
    created_at: datetime
    last_sign_in: Optional[datetime] = None

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get the current user's profile information.
    
    This endpoint returns basic information about the currently authenticated user.
    """
    return {
        "email": current_user.email,
        "name": current_user.name,
        "created_at": current_user.created_at,
        "last_sign_in": current_user.last_sign_in
    }

@router.get("/{user_id}", response_model=UserProfile)
async def get_user_by_id(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a user's profile by ID.
    
    Note: Currently, a user can only access their own profile.
    Future implementation may allow admin access to other profiles.
    """
    # Check if the requested user ID matches the current user's ID for security
    if str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only view your own profile"
        )
    
    return {
        "email": current_user.email,
        "name": current_user.name,
        "created_at": current_user.created_at,
        "last_sign_in": current_user.last_sign_in
    }