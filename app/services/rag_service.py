"""RAG (Retrieval Augmented Generation) service."""
from services.document_splitter import document_splitter
from services.embedding_service import embedding_service
from services.pgvector_store import pgvector_store
from services.reranker import reranker
from utils.logger import logger
from typing import List, Dict, Optional
import asyncio


class RAGService:
    """Manages the complete RAG pipeline: indexing and retrieval."""
    
    async def index_documents(self, documents: List[Dict], use_reranker: bool = False) -> Dict:
        """Index documents for semantic search.
        
        Args:
            documents: List of dicts with 'content' and optional metadata
            use_reranker: Whether to test reranker during indexing
            
        Returns:
            Status dict with indexing results
        """
        try:
            logger.info(f"Starting document indexing for {len(documents)} documents")
            
            # Step 1: Split documents
            chunks = document_splitter.split_documents(documents)
            logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
            
            # Step 2: Generate embeddings
            contents = [chunk['content'] for chunk in chunks]
            embeddings = embedding_service.embed_batch(contents)
            logger.info(f"Generated {len(embeddings)} embeddings")
            
            # Step 3: Store in pgvector
            doc_ids = pgvector_store.add_documents(chunks, embeddings)
            logger.info(f"Stored {len(doc_ids)} documents in pgvector")
            
            return {
                "status": "success",
                "total_documents": len(documents),
                "total_chunks": len(chunks),
                "total_embeddings": len(embeddings),
                "document_count_in_db": pgvector_store.get_document_count()
            }
            
        except Exception as e:
            logger.error(f"Error during document indexing: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def retrieve(self, query: str, top_k: Optional[int] = None, use_reranker: bool = True) -> Dict:
        """Retrieve relevant documents for a query using semantic search.
        
        Args:
            query: User query in natural language
            top_k: Number of results to return (uses settings default if None)
            use_reranker: Whether to apply reranking for better relevance
            
        Returns:
            Dict with query, results (list of dicts with content, metadata, scores), and metadata
        """
        try:
            if not query or not query.strip():
                return {
                    "status": "error",
                    "message": "Query cannot be empty"
                }
            
            top_k = top_k or 10  # Get more for reranking to choose from
            
            logger.info(f"Retrieving documents for query: {query[:100]}...")
            
            # Step 1: Generate query embedding
            query_embedding = embedding_service.embed(query)
            logger.info("Query embedding generated")
            
            # Step 2: Search in pgvector
            initial_results = pgvector_store.search(query_embedding, top_k=top_k)
            logger.info(f"Found {len(initial_results)} initial results")
            
            # Step 3: Rerank if requested
            if use_reranker and initial_results:
                final_results = reranker.rerank(query, initial_results, top_k=3)
                logger.info(f"Reranked to top {len(final_results)} results")
            else:
                final_results = initial_results[:3]
            
            return {
                "status": "success",
                "query": query,
                "results_count": len(final_results),
                "results": final_results,
                "used_reranker": use_reranker
            }
            
        except Exception as e:
            logger.error(f"Error during retrieval: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def clear_database(self) -> Dict:
        """Clear all indexed documents from database. Use with caution!"""
        try:
            pgvector_store.delete_all_documents()
            return {
                "status": "success",
                "message": "All documents have been cleared from the database"
            }
        except Exception as e:
            logger.error(f"Error clearing database: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_stats(self) -> Dict:
        """Get RAG system statistics."""
        return {
            "total_documents": pgvector_store.get_document_count(),
            "embedding_model": embedding_service.model_name,
            "embedding_dimension": embedding_service.embedding_dim,
            "reranker_model": reranker.model_name
        }


# Global instance
rag_service = RAGService()
