from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy import text
from src.app.api.router import api_router
from src.app.core.database import get_engine, Base
from src.app.core.logging import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup configuration safely after container boots.
    Ensures columns and production database tables are completely verified.
    """
    logger.info("Initializing application lifespan context...")
    try:
        engine = get_engine()
        
        # 1. First, create tables if completely missing
        Base.metadata.create_all(bind=engine)
        
        # 2. Add missing columns to existing tables safely if they don't exist
        with engine.begin() as connection:
            logger.info("Checking for missing column schemas...")
            connection.execute(text("ALTER TABLE leads ADD COLUMN IF NOT EXISTS title VARCHAR;"))
            connection.execute(text("ALTER TABLE leads ADD COLUMN IF NOT EXISTS address VARCHAR;"))
            logger.info("Schema migrations verified successfully.")
            
    except Exception as e:
        logger.error(f"Failed to verify database schemas on startup: {e}")
    
    yield
    logger.info("Shutting down application lifespan context...")

app = FastAPI(
    title="AI Lead Generation API",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(api_router)
