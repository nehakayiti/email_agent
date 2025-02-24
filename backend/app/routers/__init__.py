"""API route handlers"""
from .auth import router as auth_router
from .emails import router as emails_router
from .analytics import router as analytics_router

__all__ = ["auth_router", "emails_router", "analytics_router"] 