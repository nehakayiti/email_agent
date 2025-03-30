from contextlib import contextmanager
from contextvars import ContextVar
from app.models.user import User
from jose import jwt
from ..config import get_settings
from datetime import datetime, timedelta

settings = get_settings()
current_user: ContextVar[User] = ContextVar("current_user")

@contextmanager
def impersonation_context(user: User):
    token = current_user.set(user)
    try:
        yield
    finally:
        current_user.reset(token)

def generate_impersonation_token(user: User):
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "impersonate": True,
        "exp": datetime.utcnow() + timedelta(hours=2)  # Token valid for 2 hours
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token
