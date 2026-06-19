from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.app.core.settings import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,          # Reduced from 20 — Fargate tasks have limited connections
    max_overflow=5,        # Reduced from 10 for same reason
    pool_pre_ping=True,    # Detects stale/dropped RDS connections automatically
    pool_recycle=1800,     # Recycle connections every 30 min to avoid RDS idle timeout
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

Base = declarative_base()


def get_db():
    """FastAPI dependency: yields a DB session and ensures it is closed after request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
