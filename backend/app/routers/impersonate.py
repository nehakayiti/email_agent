from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.db import get_db
from app.models.user import User
from app.schemas.user import UserImpersonationRequest
from app.utils.impersonation import impersonation_context, generate_impersonation_token

logger = logging.getLogger(__name__)
logger.debug("Initializing impersonation router")

router = APIRouter(prefix="/api/v1", tags=["Impersonation"])

@router.post("/impersonate", status_code=status.HTTP_200_OK)
async def impersonate_user(
    request: UserImpersonationRequest,
    db: Session = Depends(get_db)
):
    logger.debug(f"Impersonation requested for user: {request.email}")

    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        logger.warning(f"Impersonation failed - User not found: {request.email}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    logger.info(f"User found for impersonation: {user.email}")

    with impersonation_context(user):
        token = generate_impersonation_token(user)
        logger.info(f"Impersonation token generated for user: {user.email}")

    return {
        "token": token,
        "message": f"Successfully impersonating user {user.email}"
    }
