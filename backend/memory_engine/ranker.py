import numpy as np
from typing import Dict, List, Tuple, Optional
import networkx as nx
from datetime import datetime, timedelta
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class MemoryRanker:
    def __init__(self, alpha: float = 0.85, time_decay_factor: float = 0.95):
        """
        Initialize the memory ranker
        
        Args:
            alpha: PageRank damping factor
            time_decay_factor: Factor for time-based decay
        """
        self.alpha = alpha
        self.time_decay_factor = time_decay_factor
    
    def calculate_pagerank(self, nodes: List[dict], edges: List[dict]) -> Dict[str, float]:
        """Calculate PageRank scores for nodes"""
        # Create NetworkX graph
        G = nx.DiGraph()
        
        # Add nodes
        for node in nodes:
            G.add_node(node['_key'], **node)
        
        # Add edges with weights
        for edge in edges:
            from_key = edge['_from'].split('/')[-1]
            to_key = edge['_to'].split('/')[-1]
            weight = edge.get('score', 1.0)
            G.add_edge(from_key, to_key, weight=weight)
        
        # Calculate PageRank
        try:
            pagerank_scores = nx.pagerank(G, alpha=self.alpha, weight='weight')
        except:
            # If graph is empty or has issues, return empty scores
            pagerank_scores = {}
        
        return pagerank_scores
    
    def calculate_time_decay(self, created_at: str, base_score: float = 1.0) -> float:
        """Calculate time decay factor for a memory"""
        try:
            # Parse creation time
            created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            current_time = datetime.utcnow()
            
            # Calculate days elapsed
            days_elapsed = (current_time - created_time).days
            
            # Apply exponential decay
            decay_factor = self.time_decay_factor ** days_elapsed
            
            return base_score * decay_factor
        except:
            return base_score
    
    def rank_memories(self, 
                     nodes: List[dict], 
                     edges: List[dict],
                     query_embedding: Optional[np.ndarray] = None,
                     node_embeddings: Optional[Dict[str, np.ndarray]] = None,
                     weights: Dict[str, float] = None) -> List[Tuple[str, float]]:
        """
        Rank memories using hybrid scoring
        
        Args:
            nodes: List of node dictionaries
            edges: List of edge dictionaries
            query_embedding: Query embedding vector
            node_embeddings: Dictionary of node embeddings
            weights: Weights for different scoring components
        
        Returns:
            List of (node_id, score) tuples sorted by score
        """
        if weights is None:
            weights = {
                'pagerank': 0.3,
                'semantic': 0.4,
                'time': 0.2,
                'degree': 0.1
            }
        
        # Calculate PageRank scores
        pagerank_scores = self.calculate_pagerank(nodes, edges)
        
        # Calculate degree centrality
        degree_scores = self._calculate_degree_centrality(nodes, edges)
        
        # Calculate time decay scores
        time_scores = {}
        for node in nodes:
            node_id = node['_key']
            created_at = node.get('created_at', '')
            time_scores[node_id] = self.calculate_time_decay(created_at)
        
        # Calculate semantic similarity scores if embeddings provided
        semantic_scores = {}
        if query_embedding is not None and node_embeddings:
            semantic_scores = self._calculate_semantic_scores(
                query_embedding, node_embeddings
            )
        
        # Combine scores
        final_scores = {}
        all_node_ids = set()
        for node in nodes:
            all_node_ids.add(node['_key'])
        
        for node_id in all_node_ids:
            score = 0.0
            
            # Add PageRank score
            if node_id in pagerank_scores:
                score += weights['pagerank'] * pagerank_scores[node_id]
            
            # Add semantic similarity score
            if node_id in semantic_scores:
                score += weights['semantic'] * semantic_scores[node_id]
            
            # Add time decay score
            if node_id in time_scores:
                score += weights['time'] * time_scores[node_id]
            
            # Add degree centrality score
            if node_id in degree_scores:
                score += weights['degree'] * degree_scores[node_id]
            
            final_scores[node_id] = score
        
        # Sort by score (descending)
        ranked_memories = sorted(
            final_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return ranked_memories
    
    def _calculate_degree_centrality(self, nodes: List[dict], edges: List[dict]) -> Dict[str, float]:
        """Calculate normalized degree centrality"""
        degree_count = defaultdict(int)
        
        for edge in edges:
            from_key = edge['_from'].split('/')[-1]
            to_key = edge['_to'].split('/')[-1]
            degree_count[from_key] += 1
            degree_count[to_key] += 1
        
        # Normalize
        max_degree = max(degree_count.values()) if degree_count else 1
        degree_scores = {
            node_id: count / max_degree 
            for node_id, count in degree_count.items()
        }
        
        return degree_scores
    
    def _calculate_semantic_scores(self, 
                                 query_embedding: np.ndarray,
                                 node_embeddings: Dict[str, np.ndarray]) -> Dict[str, float]:
        """Calculate semantic similarity scores"""
        scores = {}
        
        # Normalize query embedding
        query_norm = np.linalg.norm(query_embedding)
        if query_norm > 0:
            query_embedding = query_embedding / query_norm
        
        for node_id, node_embedding in node_embeddings.items():
            # Normalize node embedding
            node_norm = np.linalg.norm(node_embedding)
            if node_norm > 0:
                node_embedding = node_embedding / node_norm
                
                # Calculate cosine similarity
                similarity = np.dot(query_embedding, node_embedding)
                scores[node_id] = max(0, similarity)  # Ensure non-negative
            else:
                scores[node_id] = 0.0
        
        return scores
    
    def get_memory_layers(self, ranked_memories: List[Tuple[str, float]]) -> Dict[str, str]:
        """
        Assign memory layers based on scores
        
        Returns:
            Dictionary mapping node_id to memory layer
        """
        layers = {}
        total = len(ranked_memories)
        
        for i, (node_id, score) in enumerate(ranked_memories):
            percentile = i / total if total > 0 else 0
            
            if percentile < 0.1:  # Top 10%
                layers[node_id] = "immediate"
            elif percentile < 0.3:  # Top 30%
                layers[node_id] = "short_term"
            elif percentile < 0.7:  # Top 70%
                layers[node_id] = "long_term"
            else:  # Bottom 30%
                layers[node_id] = "semantic_cluster"
        
        return layers

# Singleton instance
_ranker_instance = None

def get_memory_ranker() -> MemoryRanker:
    global _ranker_instance
    if _ranker_instance is None:
        _ranker_instance = MemoryRanker()
    return _ranker_instance
