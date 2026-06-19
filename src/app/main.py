import logging
from fastapi import FastAPI
from src.app.core.logging import logger
from src.app.core.database import engine, Base
from src.app.api.router import api_router

# Import all models so SQLAlchemy registers them before create_all
import src.app.models  # noqa: F401

# Create tables if they don't exist (Alembic handles this in prod; this is a dev fallback)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Lead Generation API",
    version="0.1.0",
    description="Production-grade asynchronous real-time lead generation engine.",
)

app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    logger.info("AI Lead Qualifier API starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("AI Lead Qualifier API shutting down...")
