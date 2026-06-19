from fastapi import APIRouter
from src.app.core.database import SessionLocal
import logging

logger = logging.getLogger("lead-engine")
router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/")
def health():
    """
    Lightweight health probe for AWS ALB target group.
    Also verifies database connectivity so ECS won't route to a broken container.
    """
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        db_status = "ok"
    except Exception as e:
        logger.error(f"Health check DB ping failed: {e}")
        db_status = "error"

    return {"status": "healthy", "db": db_status}
