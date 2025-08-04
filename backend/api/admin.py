from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from pydantic import BaseModel

from ..db.arango_driver import get_arango_driver
from .auth import get_current_user, TokenData

router = APIRouter()

class ConfigUpdate(BaseModel):
    rate_limit_per_minute: Optional[int] = None
    rate_limit_per_hour: Optional[int] = None
    footer_text: Optional[str] = None
    max_memory_items: Optional[int] = None

@router.get("/config")
async def get_config(current_user: TokenData = Depends(get_current_user)):
    """Get admin configuration"""
    db = get_arango_driver()
    config_collection = db.db.collection('admin_config')
    config = config_collection.get('default')
    
    return {
        "success": True,
        "config": config
    }

@router.put("/config")
async def update_config(
    update: ConfigUpdate,
    current_user: TokenData = Depends(get_current_user)
):
    """Update admin configuration"""
    db = get_arango_driver()
    config_collection = db.db.collection('admin_config')
    
    update_dict = update.dict(exclude_none=True)
    if update_dict:
        config_collection.update({'_key': 'default'}, update_dict)
    
    return {
        "success": True,
        "message": "Configuration updated",
        "updated_fields": list(update_dict.keys())
    }

@router.post("/reset-memory")
async def reset_memory(current_user: TokenData = Depends(get_current_user)):
    """Reset all memory data"""
    db = get_arango_driver()
    db.clear_all()
    
    return {
        "success": True,
        "message": "All memory data has been cleared"
    }

@router.get("/logs")
async def get_logs(
    current_user: TokenData = Depends(get_current_user),
    limit: int = 100
):
    """Get recent query logs"""
    # TODO: Implement logging
    return {
        "success": True,
        "logs": [],
        "message": "Logging not yet implemented"
    }
