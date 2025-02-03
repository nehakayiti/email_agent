from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_emails():
    """Placeholder for email fetching endpoint"""
    return {"message": "Email fetching not implemented yet"} 