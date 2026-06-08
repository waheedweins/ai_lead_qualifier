from fastapi import APIRouter, BackgroundTasks, HTTPException
import anyio
from src.app.workers.scraping_worker import run_scraping_job

router = APIRouter(prefix="/scrape", tags=["Scraping"])

async def background_scrape(query: str):
    await anyio.to_thread.run_sync(run_scraping_job, query)

@router.post("/")
async def scrape(query: str, background_tasks: BackgroundTasks):
    if not query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")

    background_tasks.add_task(background_scrape, query)
    return {"status": "processing", "query": query}
