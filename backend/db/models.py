from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class MemoryLayer(str, Enum):
    IMMEDIATE = "immediate"
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    SEMANTIC_CLUSTER = "semantic_cluster"

class MemoryNode(BaseModel):
    id: Optional[str] = Field(None, alias="_key")
    entity: str
    entity_type: Optional[str] = None
    attributes: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True

class MemoryEdge(BaseModel):
    id: Optional[str] = Field(None, alias="_key")
    from_node: str = Field(..., alias="_from")
    to_node: str = Field(..., alias="_to")
    verb: str
    context: Optional[str] = None
    score: float = 1.0
    layer: MemoryLayer = MemoryLayer.IMMEDIATE
    polarity: float = 1.0  # -1 (negative) to 1 (positive)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = {}
    
    class Config:
        populate_by_name = True

class Triple(BaseModel):
    subject: str
    verb: str
    object: str
    context: Optional[str] = None
    confidence: float = 1.0

class MemoryQuery(BaseModel):
    query: str
    top_k: int = 10
    layer_filter: Optional[List[MemoryLayer]] = None
    time_decay: bool = True
    
class MemoryResult(BaseModel):
    nodes: List[MemoryNode]
    edges: List[MemoryEdge]
    scores: Dict[str, float]
    query_time: float
