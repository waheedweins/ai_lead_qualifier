from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from src.app.core.database import Base

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True, index=True)
    source = Column(String, nullable=True)
    status = Column(String, default="new", nullable=False)
    ai_score = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    title = Column(String, nullable=True)
    address = Column(String, nullable=True)

    agent_runs = relationship("AgentRun", back_populates="lead", cascade="all, delete-orphan")
