import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
# Import routers directly rather than through __init__.py to avoid circular imports
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
    level=logging.INFO,
    format='%(levelname)s: %(asctime)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    force=True  # This will override any existing configuration
)

# Set up more detailed logging for our app modules
app_logger = logging.getLogger('app')
app_logger.setLevel(logging.DEBUG)

# Create a file handler for important operations like email syncing
import os
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Add a rotating file handler for sync operations
sync_handler = RotatingFileHandler(
    'logs/email_sync.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
sync_handler.setLevel(logging.INFO)
sync_handler.setFormatter(logging.Formatter(
    '%(levelname)s: %(asctime)s - %(name)s - %(message)s',
    '%Y-%m-%d %H:%M:%S'
))

# Add the handler to specific loggers
for logger_name in ['app.services.email_sync_service', 'app.services.gmail', 
                   'app.services.email_processor', 'app.routers.emails']:
    logger = logging.getLogger(logger_name)
    logger.addHandler(sync_handler)
    logger.setLevel(logging.DEBUG)

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