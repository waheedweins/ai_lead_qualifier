from fastapi import FastAPI
from src.app.core.logging import logger
from src.app.api.router import api_router

import src.app.models  # noqa: F401 — registers models for Alembic autogenerate

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
