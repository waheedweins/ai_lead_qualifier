from pydantic import BaseModel, EmailStr
from datetime import datetime

class LeadCreate(BaseModel):
    name: str | None = None
    email: EmailStr
    phone: str | None = None
    source: str

class LeadResponse(BaseModel):
    id: int
    name: str | None
    email: EmailStr
    phone: str | None
    source: str
    status: str
    ai_score: int
    created_at: datetime

    model_config = {"from_attributes": True}
