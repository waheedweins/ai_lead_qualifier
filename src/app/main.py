from fastapi import FastAPI
from src.app.api.router import api_router

app = FastAPI(
    title="AI Lead Engine",
    version="1.0.0",
    docs_url="/docs"
)

app.include_router(api_router)
