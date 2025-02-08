from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .routers import auth, emails
from .db import engine, Base

settings = get_settings()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Email Agent API",
    version=settings.VERSION
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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

# Include routers
app.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"]
)

app.include_router(
    emails.router,
    prefix="/emails",
    tags=["emails"]
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"} 