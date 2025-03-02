"""API route handlers"""
# Import the router objects at usage time, not during initialization
# to avoid circular imports

__all__ = ["auth_router", "emails_router", "analytics_router"]

# The routers will be imported when they're actually used, not at module load time 