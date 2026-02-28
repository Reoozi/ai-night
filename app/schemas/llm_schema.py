from pydantic import BaseModel, Field
from typing import Optional, Literal, List, Dict, Any

class LLMRequest(BaseModel):
    prompt: str = Field(..., example="Write a short story about AI.")
    model: Literal["ollama", 'nvidia',"ragwithollama",'ragwithnvidia'] 

class LLMResponse(BaseModel):
    response: str = Field(..., example="Once upon a time, AI...")


# RAG Schemas
class DocumentInput(BaseModel):
    """Document to be indexed for RAG."""
    content: str = Field(..., example="This is document content about university administration.")
    title: Optional[str] = Field(None, example="University Admin Procedures")
    source: Optional[str] = Field(None, example="procedure_manual.pdf")
    category: Optional[str] = Field(None, example="procedures")
    metadata: Optional[Dict[str, Any]] = Field(None, example={"department": "HR"})


class IndexDocumentsRequest(BaseModel):
    """Request to index multiple documents."""
    documents: List[DocumentInput] = Field(..., example=[
        {"content": "Sample document 1", "title": "Doc 1"},
        {"content": "Sample document 2", "title": "Doc 2"}
    ])
    use_reranker: bool = Field(False, example=True)


class IndexDocumentsResponse(BaseModel):
    """Response from document indexing."""
    status: str = Field(..., example="success")
    total_documents: int
    total_chunks: int
    total_embeddings: int
    document_count_in_db: int
    message: Optional[str] = None


class RetrievalResult(BaseModel):
    """Retrieved document chunk with relevance scores."""
    id: int
    content: str = Field(..., example="Relevant passage from document...")
    metadata: Dict[str, Any]
    similarity_score: float = Field(..., example=0.87)
    rerank_score: Optional[float] = Field(None, example=0.92)


class SemanticSearchRequest(BaseModel):
    """Request for semantic search with RAG."""
    query: str = Field(..., example="How do I request leave as a university employee?")
    top_k: int = Field(3, ge=1, le=10)
    use_reranker: bool = Field(True)


class SemanticSearchResponse(BaseModel):
    """Response from semantic search."""
    status: str = Field(..., example="success")
    query: str
    results_count: int
    results: List[RetrievalResult]
    used_reranker: bool
    message: Optional[str] = None


class RAGStatsResponse(BaseModel):
    """System statistics for RAG."""
    total_documents: int
    embedding_model: str
    embedding_dimension: int
    reranker_model: str

