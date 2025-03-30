import logging
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from .config import settings, get_settings
# Import routers from __init__.py
from .routers import auth_router, users_router, emails_router, analytics_router, email_management_router, ml_router, impersonate
from .db import engine, Base
# Import models to ensure they're registered with SQLAlchemy
from .models.user import User
from .models.email import Email
from .models.email_sync import EmailSync
from .models.email_category import EmailCategory, CategoryKeyword, SenderRule
from .services.email_classifier_service import email_classifier_service
from contextlib import asynccontextmanager
from .core.logging_config import configure_logging

# Configure logging at application startup
configure_logging()
logger = logging.getLogger(__name__)
logger.info("Starting Email Agent API")

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

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan tasks (startup and shutdown)"""
    # Startup code
    logger.debug("Starting application initialization")
    
    # Create models directory if it doesn't exist
    if email_classifier_service.ensure_models_directory():
        logger.info("Models directory created/verified successfully")
    else:
        logger.warning("Failed to create/verify models directory - ML classification may not work")
    
    # Try to load trash classifier model with fallback logic
    available_models = email_classifier_service.find_available_models()
    
    if available_models:
        logger.info(f"Found {len(available_models)} classifier model(s)")
        if email_classifier_service.load_trash_classifier(None):
            logger.info("Trash classifier model loaded successfully")
        else:
            logger.warning("Failed to load any classifier model despite finding available models")
    else:
        logger.info("No trained classifier models found - this is normal for new installations")
        logger.info("The application will use rules-based classification until a model is trained")
    
    # Log the expected global model path for debugging
    model_path = email_classifier_service.get_model_path(None)
    logger.info(f"Expected global model path: {model_path}")
    
    logger.debug("Application initialization complete")
    yield
    # Shutdown code
    logger.debug("Application shutting down")

# Create FastAPI app with lifespan manager
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    debug=True,  # Enable debug mode
    lifespan=lifespan,
)

# Log middleware setup
logger.debug("Configuring CORS middleware")

# CORS middleware configuration
settings = get_settings()
# Split the CORS_ORIGINS string into a list
origins = settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS else []
logger.debug(f"Configuring CORS with origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Use the origins from settings
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
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
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(emails_router, prefix="/emails", tags=["emails"])
app.include_router(email_management_router) 
app.include_router(impersonate.router)

# Add analytics router with explicit prefix and tags
app.include_router(
    analytics_router,
    prefix="/analytics",
    tags=["analytics"]
)

# Add ML routes for model training and management
app.include_router(
    ml_router,
    prefix="/ml",
    tags=["machine-learning"]
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"} 