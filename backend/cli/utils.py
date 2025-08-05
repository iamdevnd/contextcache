import httpx
import json
from pathlib import Path
from typing import Dict, Any, Optional
from rich.console import Console

console = Console()

def get_api_client(base_url: str = "http://localhost:8000") -> httpx.Client:
    """Get HTTP client for API requests"""
    return httpx.Client(base_url=base_url, timeout=30.0)

def format_triple(subject: str, verb: str, obj: str) -> str:
   """Format a triple for display"""
   return f"{subject} --[{verb}]--> {obj}"

def format_graph_data(nodes: list, edges: list) -> Dict[str, Any]:
   """Format graph data for visualization"""
   # Create adjacency list
   graph = {}
   node_map = {node.get("_key"): node.get("entity", "Unknown") for node in nodes}
   
   for edge in edges:
       from_key = edge.get("_from", "").split("/")[-1]
       to_key = edge.get("_to", "").split("/")[-1]
       verb = edge.get("verb", "related")
       
       if from_key not in graph:
           graph[from_key] = []
       
       graph[from_key].append({
           "to": to_key,
           "verb": verb,
           "to_entity": node_map.get(to_key, to_key)
       })
   
   return {
       "nodes": node_map,
       "adjacency": graph
   }

def save_to_file(filepath: Path, data: Any, pretty: bool = True):
   """Save data to file"""
   with open(filepath, 'w') as f:
       if pretty:
           json.dump(data, f, indent=2)
       else:
           json.dump(data, f)

def load_auth_token() -> Optional[str]:
   """Load saved authentication token"""
   # In production, this would load from a secure location
   # For now, return None (no auth)
   return None

def save_auth_token(token: str):
   """Save authentication token"""
   # In production, this would save to a secure location
   pass

def format_memory_stats(stats: Dict[str, Any]) -> str:
   """Format memory statistics for display"""
   lines = []
   lines.append(f"Total Nodes: {stats.get('total_nodes', 0)}")
   lines.append(f"Total Edges: {stats.get('total_edges', 0)}")
   
   if "memory_layers" in stats:
       lines.append("\nMemory Layers:")
       for layer, count in stats["memory_layers"].items():
           lines.append(f"  {layer.replace('_', ' ').title()}: {count}")
   
   return "\n".join(lines)
