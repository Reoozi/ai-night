"""RAG API routes for document indexing and semantic search."""
from fastapi import APIRouter, HTTPException
from services.rag_service import rag_service
from schemas.llm_schema import (
    IndexDocumentsRequest,
    IndexDocumentsResponse,
    SemanticSearchRequest,
    SemanticSearchResponse,
    RAGStatsResponse
)
from utils.logger import logger

router = APIRouter()


@router.post("/index", response_model=IndexDocumentsResponse)
async def index_documents(request: IndexDocumentsRequest):
    """Index documents for semantic search.
    
    This endpoint accepts a list of documents, splits them into chunks,
    generates embeddings, and stores them in ChromaDB for semantic search.
    """
    try:
        # Convert Pydantic models to dicts
        documents = [doc.dict(exclude_none=True) for doc in request.documents]
        
        result = await rag_service.index_documents(
            documents,
            use_reranker=request.use_reranker
        )
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message"))
        
        return IndexDocumentsResponse(**result)
    
    except Exception as e:
        logger.error(f"Error in /index endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=SemanticSearchResponse)
async def semantic_search(request: SemanticSearchRequest):
    """Perform semantic search on indexed documents using RAG.
    
    This endpoint:
    1. Generates embedding for the query
    2. Searches for similar documents using cosine similarity
    3. Optionally reranks results with a cross-encoder for better relevance
    4. Returns the top 3 most relevant chunks with similarity and rerank scores
    """
    try:
        result = await rag_service.retrieve(
            query=request.query,
            top_k=request.top_k,
            use_reranker=request.use_reranker
        )
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message"))
        
        return SemanticSearchResponse(**result)
    
    except Exception as e:
        logger.error(f"Error in /search endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=RAGStatsResponse)
async def get_stats():
    """Get RAG system statistics.
    
    Returns information about:
    - Number of indexed documents
    - Embedding model being used
    - Reranker model configuration
    """
    try:
        stats = rag_service.get_stats()
        return RAGStatsResponse(**stats)
    except Exception as e:
        logger.error(f"Error in /stats endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear")
async def clear_database():
    """Clear all indexed documents from database.
    
    WARNING: This operation is irreversible. Use with caution!
    """
    try:
        result = rag_service.clear_database()
        return result
    except Exception as e:
        logger.error(f"Error in /clear endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
