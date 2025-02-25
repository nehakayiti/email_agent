import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .routers.auth import router as auth_router
from .routers.emails import router as emails_router
from .routers.analytics import router as analytics_router
from .db import engine, Base
# Import models to ensure they're registered with SQLAlchemy
from .models.user import User
from .models.email import Email
from .models.email_sync import EmailSync

# Configure logging before anything else
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s: %(asctime)s - - %(name)s - %(message)s',
    force=True  # This will override any existing configuration
)

# Explicitly set debug for our app loggers
for logger_name in ['app', 'app.routers', 'app.services', 'app.utils']:
    logging.getLogger(logger_name).setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)
logger.debug("Starting application initialization")

settings = get_settings()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    debug=True  # Enable debug mode
)

# Log middleware setup
logger.debug("Configuring CORS middleware")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": "Email Agent API",
        "version": settings.VERSION,
        "docs_url": "/docs"
    }

# Include routers with explicit prefixes and tags
app.include_router(
    auth_router,
    prefix="/auth",
    tags=["auth"]
)

app.include_router(
    emails_router,
    prefix="/emails",
    tags=["emails"]
)

# Add analytics router with explicit prefix and tags
app.include_router(
    analytics_router,
    prefix="/analytics",
    tags=["analytics"]
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"} 