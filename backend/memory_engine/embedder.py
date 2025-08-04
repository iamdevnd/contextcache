import numpy as np
from typing import List, Optional, Dict
import logging

logger = logging.getLogger(__name__)

class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the embedder with sentence transformers"""
        self.model_name = model_name
        self.model = None
        self.enabled = False
        self._initialize_model()
    
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
