from fastapi import FastAPI
from src.app.api.router import api_router
from src.app.core.database import engine
from src.app.models.base import Base  # This imports Base with models registered!

# Automatically build any missing relational tables inside your Amazon RDS database on bootup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Lead Engine",
    version="1.0.0",
    docs_url="/docs"
)

app.include_router(api_router)
