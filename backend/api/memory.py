from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from pydantic import BaseModel

from ..db.arango_driver import get_arango_driver
from ..db.models import Triple, MemoryQuery, MemoryResult
from .auth import get_current_user, TokenData

router = APIRouter()

class MemoryInsertRequest(BaseModel):
    text: str
    context: Optional[str] = None
    extract_triples: bool = True

class MemoryInsertResponse(BaseModel):
    success: bool
    triples_extracted: int
    message: str

@router.post("/insert", response_model=MemoryInsertResponse)
async def insert_memory(request: MemoryInsertRequest):
    """Insert text into memory"""
    # TODO: Implement NLP extraction
    # For now, return mock response
    return MemoryInsertResponse(
        success=True,
        triples_extracted=0,
        message="Memory insertion endpoint ready (NLP not yet implemented)"
    )

@router.post("/query")
async def query_memory(query: MemoryQuery):
    """Query the memory graph"""
    db = get_arango_driver()
    results = db.query_memories(query.query, query.top_k)
    
    return {
        "success": True,
        "query": query.query,
        "results": results
    }

@router.get("/export")
async def export_memory(current_user: TokenData = Depends(get_current_user)):
    """Export entire memory graph (admin only)"""
    db = get_arango_driver()
    stats = db.get_graph_stats()
    
    # TODO: Implement full export
    return {
        "success": True,
        "stats": stats,
        "message": "Export endpoint ready"
    }
