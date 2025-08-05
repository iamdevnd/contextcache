import numpy as np
from typing import List, Optional, Dict, Tuple
import logging
import pickle
from pathlib import Path

logger = logging.getLogger(__name__)

class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the embedder with sentence transformers and FAISS"""
        self.model_name = model_name
        self.model = None
        self.enabled = False
        self.faiss_index = None
        self.faiss_enabled = False
        self.embedding_dim = 384  # Default for MiniLM
        self.id_map = []  # Maps FAISS index to node IDs
        self._initialize_model()
        self._initialize_faiss()
    
    def _initialize_model(self):
        """Try to initialize the sentence transformer model"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            self.enabled = True
            logger.info(f"Loaded sentence transformer model: {self.model_name}")
        except ImportError:
            logger.warning("sentence-transformers not installed. Embedding disabled.")
        except Exception as e:
            logger.warning(f"Failed to load embedding model: {e}")
    
    def _initialize_faiss(self):
        """Initialize FAISS index"""
        try:
            import faiss
            # Create a simple flat index for now
            self.faiss_index = faiss.IndexFlatL2(self.embedding_dim)
            self.faiss_enabled = True
            logger.info("FAISS index initialized")
        except ImportError:
            logger.warning("FAISS not installed. Vector search disabled.")
        except Exception as e:
            logger.warning(f"Failed to initialize FAISS: {e}")
    
    def embed_text(self, text: str) -> Optional[np.ndarray]:
        """Generate embedding for a single text"""
        if not self.enabled or not text:
            return None
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    def embed_batch(self, texts: List[str]) -> List[Optional[np.ndarray]]:
        """Generate embeddings for multiple texts"""
        if not self.enabled:
            return [None] * len(texts)
        
        try:
            # Filter out empty texts
            valid_texts = [(i, t) for i, t in enumerate(texts) if t]
            if not valid_texts:
                return [None] * len(texts)
            
            # Embed valid texts
            valid_indices, valid_texts_only = zip(*valid_texts)
            embeddings = self.model.encode(list(valid_texts_only), convert_to_numpy=True)
            
            # Create result list with None for invalid texts
            results = [None] * len(texts)
            for idx, embedding in zip(valid_indices, embeddings):
                results[idx] = embedding
            
            return results
        except Exception as e:
            logger.error(f"Error in batch embedding: {e}")
            return [None] * len(texts)
    
    def add_to_index(self, node_id: str, embedding: np.ndarray):
        """Add an embedding to the FAISS index"""
        if not self.faiss_enabled or embedding is None:
            return
        
        try:
            # Ensure embedding is the right shape
            if embedding.ndim == 1:
                embedding = embedding.reshape(1, -1)
            
            # Add to FAISS index
            self.faiss_index.add(embedding)
            self.id_map.append(node_id)
            
        except Exception as e:
            logger.error(f"Error adding to FAISS index: {e}")
    
    def search_similar(self, 
                      query_embedding: np.ndarray, 
                      k: int = 10) -> List[Tuple[str, float]]:
        """Search for similar embeddings using FAISS"""
        if not self.faiss_enabled or query_embedding is None:
            return []
        
        try:
            # Ensure query embedding is the right shape
            if query_embedding.ndim == 1:
                query_embedding = query_embedding.reshape(1, -1)
            
            # Search in FAISS
            distances, indices = self.faiss_index.search(query_embedding, k)
            
            # Convert to (node_id, similarity_score) tuples
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.id_map):
                    # Convert L2 distance to similarity score (inverse)
                    similarity = 1.0 / (1.0 + distances[0][i])
                    results.append((self.id_map[idx], similarity))
            
            return results
        
        except Exception as e:
            logger.error(f"Error searching FAISS index: {e}")
            return []
    
    def build_index_from_nodes(self, nodes: List[Dict[str, any]]):
        """Build FAISS index from a list of nodes"""
        if not self.enabled or not self.faiss_enabled:
            return
        
        # Clear existing index
        self._initialize_faiss()
        self.id_map = []
        
        for node in nodes:
            node_id = node.get('_key')
            text = node.get('entity', '')
            
            if node_id and text:
                embedding = self.embed_text(text)
                if embedding is not None:
                    self.add_to_index(node_id, embedding)
        
        logger.info(f"Built FAISS index with {len(self.id_map)} embeddings")
    
    def save_index(self, path: Path):
        """Save FAISS index and mappings to disk"""
        if not self.faiss_enabled:
            return
        
        try:
            import faiss
            # Save FAISS index
            faiss.write_index(self.faiss_index, str(path / "faiss.index"))
            
            # Save ID mappings
            with open(path / "id_map.pkl", 'wb') as f:
                pickle.dump(self.id_map, f)
                
            logger.info(f"Saved FAISS index to {path}")
            
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}")
    
    def load_index(self, path: Path):
        """Load FAISS index and mappings from disk"""
        if not self.faiss_enabled:
            return
        
        try:
            import faiss
            # Load FAISS index
            self.faiss_index = faiss.read_index(str(path / "faiss.index"))
            
            # Load ID mappings
            with open(path / "id_map.pkl", 'rb') as f:
                self.id_map = pickle.load(f)
                
            logger.info(f"Loaded FAISS index from {path}")
            
        except Exception as e:
            logger.error(f"Error loading FAISS index: {e}")
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Compute cosine similarity between two embeddings"""
        if embedding1 is None or embedding2 is None:
            return 0.0
        
        # Normalize vectors
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # Compute cosine similarity
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
        return float(similarity)

# Singleton instance
_embedder_instance = None

def get_embedder() -> Embedder:
    global _embedder_instance
    if _embedder_instance is None:
        from ..config import get_settings
        settings = get_settings()
        _embedder_instance = Embedder(settings.embedding_model)
    return _embedder_instance
