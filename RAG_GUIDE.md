# RAG System - Complete Implementation Guide

## Overview

This RAG (Retrieval Augmented Generation) system provides semantic search capabilities for your application. It allows you to:

1. **Index documents** - Split documents into chunks and store embeddings in pgvector
2. **Semantic search** - Find relevant documents using natural language queries
3. **Rerank results** - Improve relevance using a cross-encoder model
4. **Augment LLM prompts** - Use retrieved context to enhance LLM responses

## Architecture

```
User Query
    ↓
Embedding Service (sentence-transformers)
    ↓
Vector Search (pgvector - cosine similarity)
    ↓
Top-K Results (retrieved chunks)
    ↓
Reranker (cross-encoder for better relevance)
    ↓
Final Results (top 3 relevant chunks with scores)
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

The new dependencies added:

- `pgvector` - PostgreSQL vector extension
- `sentence-transformers` - Embedding generation
- `psycopg2-binary` - PostgreSQL adapter
- `scipy`, `numpy` - Mathematical operations
- `langchain-postgres` - PostgreSQL integration

### 2. Set up PostgreSQL with pgvector

Option A: Using Docker (recommended)

```bash
docker-compose -f docker/docker-compose.yml up -d
```

Option B: Manual setup

- Install PostgreSQL 12+
- Install pgvector extension
- Create database: `create database rag_db;`

### 3. Configure Environment Variables

Create a `.env` file:

```env
# PostgreSQL/pgvector
PGVECTOR_HOST=localhost
PGVECTOR_PORT=5432
PGVECTOR_DB=rag_db
PGVECTOR_USER=postgres
PGVECTOR_PASSWORD=password

# Embedding Model (using sentence-transformers)
EMBEDDING_MODEL=all-MiniLM-L6-v2
# Other options:
# - all-mpnet-base-v2 (larger, more accurate)
# - paraphrase-MiniLM-L6-v2 (good for paraphrasing)

# Document Splitting
CHUNK_SIZE=500
CHUNK_OVERLAP=50

# Retrieval
TOP_K_RESULTS=3

# NVIDIA API
NVIDIA_API_KEY=your_key_here
```

## API Endpoints

### 1. Index Documents

**Endpoint:** `POST /rag/index`

Index documents for semantic search:

```bash
curl -X POST "http://localhost:8000/rag/index" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {
        "content": "University leave request procedures: Employees can request leave through the HR portal...",
        "title": "Leave Procedures",
        "source": "hr_manual.pdf",
        "category": "procedures"
      },
      {
        "content": "Salary payment is processed on the last working day of each month...",
        "title": "Salary Information",
        "source": "payment_guide.pdf",
        "category": "finance"
      }
    ],
    "use_reranker": false
  }'
```

**Response:**

```json
{
  "status": "success",
  "total_documents": 2,
  "total_chunks": 12,
  "total_embeddings": 12,
  "document_count_in_db": 12
}
```

### 2. Semantic Search

**Endpoint:** `POST /rag/search`

Search for relevant documents:

```bash
curl -X POST "http://localhost:8000/rag/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I request leave as a university employee?",
    "top_k": 3,
    "use_reranker": true
  }'
```

**Response:**

```json
{
  "status": "success",
  "query": "How do I request leave as a university employee?",
  "results_count": 3,
  "used_reranker": true,
  "results": [
    {
      "id": 1,
      "content": "Employees can request leave through the HR portal...",
      "metadata": {
        "title": "Leave Procedures",
        "category": "procedures"
      },
      "similarity_score": 0.87,
      "rerank_score": 0.92
    },
    {
      "id": 2,
      "content": "Leave types include annual, sick, and unpaid leave...",
      "metadata": {
        "title": "Leave Types",
        "category": "procedures"
      },
      "similarity_score": 0.82,
      "rerank_score": 0.88
    },
    {
      "id": 3,
      "content": "Approval is typically given within 2 business days...",
      "metadata": {
        "title": "Leave Approval Timeline",
        "category": "procedures"
      },
      "similarity_score": 0.75,
      "rerank_score": 0.81
    }
  ]
}
```

### 3. RAG-Augmented LLM Query

**Endpoint:** `POST /llm/retrivel`

Use RAG context with LLM:

```bash
curl -X POST "http://localhost:8000/llm/retrivel" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "How do I request leave?",
    "model": "ragwithnvidia"
  }'
```

The system will:

1. Retrieve top 3 relevant documents
2. Augment the prompt with retrieved context
3. Send augmented prompt to NVIDIA LLM
4. Return enhanced response

### 4. Get Statistics

**Endpoint:** `GET /rag/stats`

```bash
curl "http://localhost:8000/rag/stats"
```

**Response:**

```json
{
  "total_documents": 12,
  "embedding_model": "all-MiniLM-L6-v2",
  "embedding_dimension": 384,
  "reranker_model": "cross-encoder/ms-marco-MiniLM-L-12-v2"
}
```

### 5. Clear Database

**Endpoint:** `DELETE /rag/clear`

```bash
curl -X DELETE "http://localhost:8000/rag/clear"
```

## Key Components

### 1. DocumentSplitter (`services/document_splitter.py`)

- Splits large documents into overlapping chunks
- Preserves metadata through the chunking process
- Uses RecursiveCharacterTextSplitter for intelligent splitting

### 2. EmbeddingService (`services/embedding_service.py`)

- Generates semantic embeddings using sentence-transformers
- Supports batch embedding for efficiency
- Calculates cosine similarity between vectors

### 3. PgVectorStore (`services/pgvector_store.py`)

- Manages vector storage in PostgreSQL
- Uses pgvector extension for efficient similarity search
- Includes IVFFlat indexing for fast retrieval

### 4. Reranker (`services/reranker.py`)

- Uses cross-encoder models for better relevance
- Reranks initial search results
- Significantly improves answer quality

### 5. RAGService (`services/rag_service.py`)

- Orchestrates the complete RAG pipeline
- Handles document indexing
- Manages retrieval and reranking

## Usage Examples

### Example 1: Basic Document Indexing and Search

```python
from services.rag_service import rag_service
import asyncio

async def example_basic():
    # Index documents
    documents = [
        {
            "content": "Python is a programming language.",
            "title": "Python Intro",
            "category": "programming"
        },
        {
            "content": "Machine learning is a subset of artificial intelligence.",
            "title": "ML Intro",
            "category": "ai"
        }
    ]

    index_result = await rag_service.index_documents(documents)
    print(f"Indexed: {index_result['total_chunks']} chunks")

    # Search
    search_result = await rag_service.retrieve(
        query="Tell me about Python",
        use_reranker=True
    )

    for result in search_result['results']:
        print(f"- {result['content'][:100]}...")
        print(f"  Similarity: {result['similarity_score']:.2f}")
        print(f"  Rerank Score: {result.get('rerank_score', 'N/A')}\n")

asyncio.run(example_basic())
```

### Example 2: RAG with LLM

```python
from services.llm_router import get_llm_response
import asyncio

async def example_rag_llm():
    # This uses RAG to augment the LLM prompt
    response = await get_llm_response(
        prompt="What are the leave policies?",
        model="ragwithnvidia"
    )
    print(response)

asyncio.run(example_rag_llm())
```

## Performance Tuning

### 1. Chunk Size vs Search Quality

- Smaller chunks: More precise but may miss context
- Larger chunks: More context but less precise
- Recommended: 500 tokens with 50 token overlap

### 2. Reranker vs Speed

- Reranking improves quality significantly (5-10% boost)
- Adds ~200-500ms latency
- Use `use_reranker=True` for production

### 3. Embedding Model Selection

- `all-MiniLM-L6-v2`: Fast, good quality (384 dims)
- `all-mpnet-base-v2`: Better quality, slower (768 dims)
- `paraphrase-MiniLM-L6-v2`: Good for paraphrasing

### 4. Database Optimization

- IVFFlat index is configured with `lists=100`
- For >10M documents, increase lists to 1000
- Periodic VACUUM ANALYZE on large databases

## Troubleshooting

### Issue: "Failed to connect to database"

Solution:

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check connection
psql -h localhost -U postgres -d rag_db

# Verify pgvector is installed
psql -h localhost -U postgres -d rag_db -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Issue: "CUDA out of memory" (if using GPU)

Solution:

- Reduce `batch_size` in `embed_batch()`
- Use smaller embedding model
- Process documents in smaller batches

### Issue: Low search quality

Solution:

1. Increase `chunk_size` for more context
2. Reduce `chunk_overlap` if too much repetition
3. Use larger embedding model (`all-mpnet-base-v2`)
4. Enable reranking (`use_reranker=True`)

## Production Deployment Checklist

- [ ] PostgreSQL configured with proper backups
- [ ] Embedding model cached locally
- [ ] Connection pooling configured
- [ ] Monitoring and logging in place
- [ ] Rate limiting on API endpoints
- [ ] Document versioning strategy defined
- [ ] Regular database maintenance scheduled
- [ ] HTTPS enabled
- [ ] Authentication/authorization implemented

## Environment Variables Reference

| Variable          | Default          | Description                  |
| ----------------- | ---------------- | ---------------------------- |
| PGVECTOR_HOST     | localhost        | PostgreSQL host              |
| PGVECTOR_PORT     | 5432             | PostgreSQL port              |
| PGVECTOR_DB       | rag_db           | Database name                |
| PGVECTOR_USER     | postgres         | Database user                |
| PGVECTOR_PASSWORD | password         | Database password            |
| EMBEDDING_MODEL   | all-MiniLM-L6-v2 | Sentence-transformers model  |
| CHUNK_SIZE        | 500              | Document chunk size (tokens) |
| CHUNK_OVERLAP     | 50               | Chunk overlap (tokens)       |
| TOP_K_RESULTS     | 3                | Default number of results    |
| NVIDIA_API_KEY    |                  | NVIDIA API key for LLM       |

## Next Steps

1. **Start the services**: `python app/main.py`
2. **Index your documents**: POST to `/rag/index`
3. **Test search**: POST to `/rag/search`
4. **Integrate with LLM**: Use `ragwithnvidia` model
5. **Monitor performance**: Check `/rag/stats`

## Performance Metrics

Typical performance (on standard hardware):

- Embedding generation: ~50-100 docs/sec
- Vector search: <100ms for 10K documents
- Reranking: ~200-500ms for top-10 results
- End-to-end RAG query: <1 second

---

For more details, refer to the source code documentation in `app/services/`.
