"""API route handlers"""
# Import the router objects at usage time, not during initialization
# to avoid circular imports

__all__ = ["auth_router", "emails_router", "analytics_router", "users_router", "email_management_router", "ml_router", "action_management_router", "proposed_actions_router"]

# The routers will be imported when they're actually used, not at module load time
from .auth import router as auth_router
from .emails import router as emails_router
from .analytics import router as analytics_router
from .users import router as users_router
from .email_management import router as email_management_router
from .ml_routes import router as ml_router
from .action_management import router as action_management_router
from .proposed_actions import router as proposed_actions_router