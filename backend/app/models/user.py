from sqlalchemy import Column, String, DateTime, JSON, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from ..db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_sign_in = Column(DateTime(timezone=True))
    credentials = Column(JSON) 