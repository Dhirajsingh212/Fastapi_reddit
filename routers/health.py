from fastapi import APIRouter
from sqlalchemy import text
from dependency import db_dependency

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check(db: db_dependency):
    """Health check endpoint"""
    try:
        # Check database
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "version": "0.1.1"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

@router.get("/metrics")
async def metrics():
    """Basic metrics endpoint"""
    # Integrate with Prometheus client if needed
    return {"uptime": "TODO", "requests": "TODO"}