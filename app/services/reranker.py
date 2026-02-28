"""Reranking service for improving search result relevance."""
from sentence_transformers import CrossEncoder
import numpy as np
from core.config import settings
from utils.logger import logger
from typing import List, Dict


class Reranker:
    """Reranks search results using a cross-encoder model for better relevance."""
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-12-v2"):
        """Initialize reranker with a cross-encoder model.
        
        Args:
            model_name: Name of the cross-encoder model from Hugging Face
        """
        self.model_name = model_name
        
        try:
            logger.info(f"Loading reranker model: {self.model_name}")
            self.model = CrossEncoder(self.model_name)
            logger.info("Reranker model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load reranker model: {str(e)}")
            raise
    
    def rerank(self, query: str, documents: List[Dict], top_k: int = 3) -> List[Dict]:
        """Rerank documents based on relevance to the query.
        
        Args:
            query: User query
            documents: List of dicts with 'id', 'content', 'similarity_score', 'metadata'
            top_k: Number of results to return after reranking
            
        Returns:
            Reranked list of documents with updated 'rerank_score'
        """
        if not documents:
            logger.warning("Empty document list provided for reranking")
            return []
        
        try:
            # Prepare query-document pairs
            pairs = [[query, doc['content']] for doc in documents]
            
            # Get rerank scores
            rerank_scores = self.model.predict(pairs)
            
            # Update documents with rerank scores
            for doc, score in zip(documents, rerank_scores):
                doc['rerank_score'] = float(score)
            
            # Sort by rerank score
            reranked = sorted(documents, key=lambda x: x['rerank_score'], reverse=True)
            
            # Return top_k results
            result = reranked[:top_k]
            logger.info(f"Reranked {len(documents)} documents, returning top {len(result)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error during reranking: {str(e)}")
            # Return original order if reranking fails
            return documents[:top_k]
    
    def batch_rerank(self, queries: List[str], documents: List[List[Dict]], top_k: int = 3) -> List[List[Dict]]:
        """Rerank multiple queries with their documents.
        
        Args:
            queries: List of queries
            documents: List of document lists (one per query)
            top_k: Number of results per query
            
        Returns:
            List of reranked document lists
        """
        results = []
        for query, docs in zip(queries, documents):
            results.append(self.rerank(query, docs, top_k))
        return results


# Global instance
reranker = Reranker()
