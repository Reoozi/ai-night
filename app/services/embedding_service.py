"""Embedding service for semantic search."""
from sentence_transformers import SentenceTransformer
import numpy as np
from core.config import settings
from utils.logger import logger
from typing import List, Union


class EmbeddingService:
    """Generates embeddings for text using sentence transformers."""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.embedding_model
        
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"Embedding model loaded with dimension: {self.embedding_dim}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}")
            raise
    
    def embed(self, text: Union[str, List[str]]) -> Union[np.ndarray, List[np.ndarray]]:
        """Generate embedding for text(s).
        
        Args:
            text: Single string or list of strings
            
        Returns:
            Embedding(s) as numpy array(s)
        """
        try:
            if isinstance(text, str):
                embedding = self.model.encode(text, convert_to_numpy=True)
                return embedding
            else:
                embeddings = self.model.encode(text, convert_to_numpy=True)
                return embeddings
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[np.ndarray]:
        """Generate embeddings for a batch of texts efficiently."""
        try:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=True
            )
            return embeddings
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            raise
    
    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(np.dot(vec1, vec2) / (norm1 * norm2))


# Global instance
embedding_service = EmbeddingService()
