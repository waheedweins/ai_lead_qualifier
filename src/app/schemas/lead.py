from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class LeadCreate(BaseModel):
    name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    source: Optional[str] = "apify"  # ✅ Made optional with a default value
    title: Optional[str] = None
    address: Optional[str] = None

class LeadResponse(BaseModel):
    id: int
    name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    source: Optional[str] = None      # ✅ Fixed: Made Optional to prevent 500 error on NULL values
    status: str
    ai_score: int
    title: Optional[str] = None       # ✅ Added: Exposes the business title in responses
    address: Optional[str] = None     # ✅ Added: Exposes the full business address
    created_at: datetime

    model_config = {"from_attributes": True}
