from pydantic import BaseModel, EmailStr

class UserImpersonationRequest(BaseModel):
    email: EmailStr
