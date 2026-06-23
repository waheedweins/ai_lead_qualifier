from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.app.core.settings import settings

# Global placeholders for lazy initialization
_engine = None
_SessionLocal = None

Base = declarative_base()

def get_engine():
    """Dynamically initializes the SQLAlchemy engine when first requested."""
    global _engine
    if _engine is None:
        if not settings.DATABASE_URL:
            raise ValueError("DATABASE_URL is missing or has not been loaded from Secrets Manager yet.")
        
        _engine = create_engine(
            settings.DATABASE_URL,
            pool_size=10,          # Optimized for Fargate container connection limits
            max_overflow=5,        # Keeps a tight connection boundary
            pool_pre_ping=True,    # Safely detects and drops stale RDS connections
            pool_recycle=1800,     # Recycles connection pool every 30 minutes
        )
    return _engine

def get_sessionmaker():
    """Dynamically initializes the sessionmaker bound to the lazy engine."""
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(
            bind=engine,
            autoflush=False,
            autocommit=False,
        )
    return _SessionLocal

def get_db():
    """
    FastAPI dependency context provider: Yields an active transactional 
    database session context and safely closes it post-execution lifecycle.
    """
    SessionLocal = get_sessionmaker()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
