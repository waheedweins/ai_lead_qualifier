from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class LeadCreate(BaseModel):
    name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    source: str
    title: Optional[str] = None
    address: Optional[str] = None

class LeadResponse(BaseModel):
    id: int
    name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    source: str
    status: str
    ai_score: int
    created_at: datetime

    model_config = {"from_attributes": True}
