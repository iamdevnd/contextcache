from fastapi import APIRouter, HTTPException
from ..db.arango_driver import get_arango_driver
from typing import Dict

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    db = get_arango_driver()
    
    if not db.health_check():
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    return {
        "status": "healthy",
        "database": "connected"
    }

@router.get("/stats")
async def get_stats() -> Dict[str, any]:
    """Get system statistics"""
    db = get_arango_driver()
    stats = db.get_graph_stats()
    
    return {
        "status": "ok",
        "stats": stats
    }
