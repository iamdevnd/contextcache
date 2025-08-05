from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
from ..memory_engine.ranker import get_memory_ranker

from ..db.arango_driver import get_arango_driver
from ..db.models import Triple, MemoryQuery, MemoryResult, MemoryNode, MemoryEdge, MemoryLayer
from ..memory_engine.extractor import get_triple_extractor
from ..memory_engine.embedder import get_embedder
from .auth import get_current_user, TokenData

router = APIRouter()

class MemoryInsertRequest(BaseModel):
    text: str
    context: Optional[str] = None
    extract_triples: bool = True

class MemoryInsertResponse(BaseModel):
    success: bool
    triples_extracted: int
    nodes_created: int
    edges_created: int
    message: str

@router.post("/insert", response_model=MemoryInsertResponse)
async def insert_memory(request: MemoryInsertRequest):
    """Insert text into memory"""
    db = get_arango_driver()
    extractor = get_triple_extractor()
    
    nodes_created = 0
    edges_created = 0
    triples_extracted = 0
    
    if request.extract_triples and extractor.enabled:
        # Extract triples
        triples = extractor.extract_triples(request.text, request.context)
        triples_extracted = len(triples)
        
        # Store each triple in the graph
        for triple in triples:
            # Create or update subject node
            subject_node = MemoryNode(
                entity=triple.subject,
                entity_type="entity",
                attributes={"source": "extraction"}
            )
            subject_id = db.insert_node(subject_node)
            if "mem_nodes/" in subject_id:
                nodes_created += 1
            
            # Create or update object node
            object_node = MemoryNode(
                entity=triple.object,
                entity_type="entity",
                attributes={"source": "extraction"}
            )
            object_id = db.insert_node(object_node)
            if "mem_nodes/" in object_id:
                nodes_created += 1
            
            # Create edge
            edge = MemoryEdge(
                from_node=subject_id,
                to_node=object_id,
                verb=triple.verb,
                context=triple.context,
                score=triple.confidence,
                layer=MemoryLayer.IMMEDIATE,
                polarity=1.0,
                metadata={"extracted_from": request.text[:100]}
            )
            edge_id = db.insert_edge(edge)
            edges_created += 1
    
    # Also store the full text as a document node
    text_node = MemoryNode(
        entity=request.text[:100] + "..." if len(request.text) > 100 else request.text,
        entity_type="document",
        attributes={
            "full_text": request.text,
            "context": request.context,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    db.insert_node(text_node)
    nodes_created += 1
    
    return MemoryInsertResponse(
        success=True,
        triples_extracted=triples_extracted,
        nodes_created=nodes_created,
        edges_created=edges_created,
        message=f"Successfully processed memory. Extracted {triples_extracted} triples."
    )

@router.post("/query")
async def query_memory(query: MemoryQuery):
    """Query the memory graph"""
    db = get_arango_driver()
    embedder = get_embedder()
    
    # Get basic graph results
    results = db.query_memories(query.query, query.top_k)
    
    # TODO: Add embedding-based similarity search
    # TODO: Add ranking and scoring
    
    return {
        "success": True,
        "query": query.query,
        "results": results,
        "embedding_enabled": embedder.enabled
    }

@router.get("/stats")
async def get_memory_stats():
    """Get memory statistics"""
    db = get_arango_driver()
    stats = db.get_graph_stats()
    
    return {
        "success": True,
        "stats": stats
    }

@router.delete("/clear")
async def clear_memory(current_user: TokenData = Depends(get_current_user)):
    """Clear all memory (admin only)"""
    db = get_arango_driver()
    db.clear_all()
    
    return {
        "success": True,
        "message": "All memory cleared successfully"
    }

@router.get("/export")
async def export_memory(current_user: TokenData = Depends(get_current_user)):
    """Export entire memory graph (admin only)"""
    db = get_arango_driver()
    
    # Get all nodes and edges
    nodes_collection = db.db.collection('mem_nodes')
    edges_collection = db.db.collection('mem_edges')
    
    all_nodes = list(nodes_collection.find({}, limit=1000))
    all_edges = list(edges_collection.find({}, limit=1000))
    
    return {
        "success": True,
        "export": {
            "nodes": all_nodes,
            "edges": all_edges,
            "metadata": {
                "exported_at": datetime.utcnow().isoformat(),
                "node_count": len(all_nodes),
                "edge_count": len(all_edges)
            }
        }
    }

# Add this new endpoint to backend/api/memory.py
# Add it after the existing endpoints

@router.get("/graph")
async def get_graph_data(limit: int = 100):
    """Get graph data for visualization"""
    db = get_arango_driver()
    
    # Get nodes and edges
    nodes_collection = db.db.collection('mem_nodes')
    edges_collection = db.db.collection('mem_edges')
    
    nodes = list(nodes_collection.find({}, limit=limit))
    edges = list(edges_collection.find({}, limit=limit))
    
    # Convert to format expected by frontend
    graph_data = {
        "nodes": [
            {
                "_key": node["_key"],
                "entity": node.get("entity", ""),
                "entity_type": node.get("entity_type", "entity")
            }
            for node in nodes
        ],
        "edges": [
            {
                "_from": edge["_from"],
                "_to": edge["_to"],
                "verb": edge.get("verb", "related"),
                "score": edge.get("score", 1.0)
            }
            for edge in edges
        ]
    }
    
    return {
        "success": True,
        "graph": graph_data
    }

@router.post("/query/advanced")
async def advanced_query(
    query: MemoryQuery,
    use_semantic: bool = True,
    use_pagerank: bool = True,
    use_time_decay: bool = True
):
    """Advanced query with ranking algorithms"""
    db = get_arango_driver()
    embedder = get_embedder()
    ranker = get_memory_ranker()
    
    # Get all nodes and edges for ranking
    nodes_collection = db.db.collection('mem_nodes')
    edges_collection = db.db.collection('mem_edges')
    
    # First, do a basic search to get candidate nodes
    basic_results = db.query_memories(query.query, query.top_k * 3)  # Get more candidates
    
    if not basic_results['results']:
        return {
            "success": True,
            "query": query.query,
            "results": [],
            "ranking_enabled": True
        }
    
    # Get all nodes and edges for ranking
    all_nodes = list(nodes_collection.find({}, limit=1000))
    all_edges = list(edges_collection.find({}, limit=1000))
    
    # Prepare for ranking
    query_embedding = None
    node_embeddings = {}
    
    if use_semantic and embedder.enabled:
        # Get query embedding
        query_embedding = embedder.embed_text(query.query)
        
        # Get embeddings for all nodes
        for node in all_nodes:
            node_id = node['_key']
            text = node.get('entity', '')
            if text:
                embedding = embedder.embed_text(text)
                if embedding is not None:
                    node_embeddings[node_id] = embedding
    
    # Configure ranking weights
    weights = {
        'pagerank': 0.3 if use_pagerank else 0.0,
        'semantic': 0.4 if use_semantic else 0.0,
        'time': 0.2 if use_time_decay else 0.0,
        'degree': 0.1
    }
    
    # Normalize weights
    total_weight = sum(weights.values())
    if total_weight > 0:
        weights = {k: v/total_weight for k, v in weights.items()}
    
    # Rank memories
    ranked_memories = ranker.rank_memories(
        all_nodes,
        all_edges,
        query_embedding,
        node_embeddings,
        weights
    )
    
    # Get top K results
    top_results = []
    node_map = {node['_key']: node for node in all_nodes}
    
    for node_id, score in ranked_memories[:query.top_k]:
        if node_id in node_map:
            node = node_map[node_id]
            # Get edges for this node
            node_edges = [
                edge for edge in all_edges 
                if edge['_from'].endswith(node_id) or edge['_to'].endswith(node_id)
            ]
            
            top_results.append({
                'node': node,
                'edges': node_edges,
                'score': score
            })
    
    return {
        "success": True,
        "query": query.query,
        "results": {
            "results": top_results,
            "count": len(top_results)
        },
        "ranking_enabled": True,
        "algorithms_used": {
            "semantic": use_semantic and embedder.enabled,
            "pagerank": use_pagerank,
            "time_decay": use_time_decay
        }
    }

@router.post("/index/rebuild")
async def rebuild_search_index(current_user: TokenData = Depends(get_current_user)):
    """Rebuild the FAISS search index (admin only)"""
    db = get_arango_driver()
    embedder = get_embedder()
    
    if not embedder.faiss_enabled:
        return {
            "success": False,
            "message": "FAISS not available"
        }
    
    # Get all nodes
    nodes_collection = db.db.collection('mem_nodes')
    all_nodes = list(nodes_collection.find({}, limit=10000))
    
    # Build index
    embedder.build_index_from_nodes(all_nodes)
    
    return {
        "success": True,
        "message": f"Rebuilt index with {len(all_nodes)} nodes"
    }