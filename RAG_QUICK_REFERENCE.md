# RAG System - Quick Reference Guide

## 🚀 Getting Started in 5 Minutes

### 1. Start PostgreSQL

```bash
cd docker
docker-compose up -d
# Wait for postgres to be healthy (~10 seconds)
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env if needed (defaults work for local testing)
```

### 4. Run the Application

```bash
python app/main.py
```

### 5. Test RAG

```bash
# In another terminal, create sample documents
curl -X POST "http://localhost:8000/rag/index" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {"content": "Python is a programming language.", "title": "Python"},
      {"content": "Machine learning uses algorithms.", "title": "ML"}
    ]
  }'

# Search
curl -X POST "http://localhost:8000/rag/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Python?", "use_reranker": true}'
```

---

## 📚 Core APIs

### POST `/rag/index`

Index documents for semantic search

**Request:**

```json
{
  "documents": [
    {
      "content": "Document text",
      "title": "Title",
      "source": "source.pdf",
      "category": "category",
      "metadata": { "any": "field" }
    }
  ],
  "use_reranker": true
}
```

**Response:**

```json
{
  "status": "success",
  "total_documents": 1,
  "total_chunks": 5,
  "total_embeddings": 5,
  "document_count_in_db": 5
}
```

---

### POST `/rag/search`

Semantic search with reranking

**Request:**

```json
{
  "query": "Your question here",
  "top_k": 3,
  "use_reranker": true
}
```

**Response:**

```json
{
  "status": "success",
  "query": "Your question here",
  "results_count": 3,
  "used_reranker": true,
  "results": [
    {
      "id": 1,
      "content": "Relevant text...",
      "metadata": { "title": "Source Title" },
      "similarity_score": 0.87,
      "rerank_score": 0.92
    }
  ]
}
```

---

### GET `/rag/stats`

Get system statistics

**Response:**

```json
{
  "total_documents": 10,
  "embedding_model": "all-MiniLM-L6-v2",
  "embedding_dimension": 384,
  "reranker_model": "cross-encoder/ms-marco-MiniLM-L-12-v2"
}
```

---

### DELETE `/rag/clear`

Clear all documents (⚠️ irreversible)

---

### POST `/llm/retrivel`

Query LLM with RAG augmentation

**Request:**

```json
{
  "prompt": "Your question",
  "model": "ragwithnvidia" // or "ragwithollama"
}
```

**Response:**

```json
{
  "response": "Generated answer using context..."
}
```

---

## 🔧 Service Classes

### RAGService

Main orchestrator for RAG pipeline

```python
from services.rag_service import rag_service
import asyncio

async def example():
    # Index
    await rag_service.index_documents([
        {"content": "Document text", "title": "Title"}
    ])

    # Search
    result = await rag_service.retrieve(
        query="Your question",
        top_k=3,
        use_reranker=True
    )

    # Stats
    stats = rag_service.get_stats()

    # Clear
    rag_service.clear_database()

asyncio.run(example())
```

### DocumentSplitter

Split documents into chunks

```python
from services.document_splitter import document_splitter

chunks = document_splitter.split_text("Large document text...")
# Returns: ["chunk1", "chunk2", ...]

chunks_with_meta = document_splitter.split_documents([
    {"content": "text", "title": "Title"}
])
```

### EmbeddingService

Generate embeddings

```python
from services.embedding_service import embedding_service

# Single text
embedding = embedding_service.embed("Some text")

# Multiple texts
embeddings = embedding_service.embed_batch([
    "Text 1", "Text 2"
])

# Similarity
score = embedding_service.cosine_similarity(vec1, vec2)
```

### PgVectorStore

Vector storage operations

```python
from services.pgvector_store import pgvector_store

# Add documents
doc_ids = pgvector_store.add_documents(
    documents=[{"content": "text"}],
    embeddings=[embedding_vector]
)

# Search
results = pgvector_store.search(
    query_embedding=query_vector,
    top_k=3
)

# Stats
count = pgvector_store.get_document_count()

# Clear
pgvector_store.delete_all_documents()
```

### Reranker

Improve ranking with cross-encoders

```python
from services.reranker import reranker

results = reranker.rerank(
    query="Question",
    documents=[doc1, doc2, ...],
    top_k=3
)
# Returns reranked documents with rerank_score
```

---

## 🎨 Models & Configuration

### Embedding Models

```env
# Fast (default)
EMBEDDING_MODEL=all-MiniLM-L6-v2
# Dimensions: 384, Speed: Fast, Quality: Good

# Better quality
EMBEDDING_MODEL=all-mpnet-base-v2
# Dimensions: 768, Speed: Medium, Quality: Excellent

# Paraphrasing
EMBEDDING_MODEL=paraphrase-MiniLM-L6-v2
# Dimensions: 384, Speed: Fast, Quality: Good
```

### Document Chunking

```env
# Small chunks = More precise
CHUNK_SIZE=300
CHUNK_OVERLAP=30

# Large chunks = More context
CHUNK_SIZE=1000
CHUNK_OVERLAP=100

# Default
CHUNK_SIZE=500
CHUNK_OVERLAP=50
```

### Reranker

Model: `cross-encoder/ms-marco-MiniLM-L-12-v2`

- Adds 200-500ms latency
- 5-10% quality improvement
- Recommended for production

---

## 🐛 Common Issues & Solutions

| Issue                       | Cause                | Solution                              |
| --------------------------- | -------------------- | ------------------------------------- |
| PostgreSQL connection error | Docker not running   | `docker-compose up -d`                |
| "No module named pgvector"  | Missing dependencies | `pip install -r requirements.txt`     |
| Low search quality          | Poor chunks/model    | Enable reranker or try larger model   |
| Slow searches               | No index             | Recreate index (automatic on startup) |
| CUDA out of memory          | GPU limited          | Use CPU or reduce batch size          |

## 🔍 Database Queries

```bash
# Connect to database
psql -h localhost -U postgres -d rag_db

# Check documents
SELECT id, LEFT(content, 50) as preview, jsonb_pretty(metadata) FROM documents LIMIT 5;

# Count documents
SELECT COUNT(*) FROM documents;

# Check index
SELECT indexname FROM pg_indexes WHERE tablename = 'documents';

# Clear all
TRUNCATE documents;
```

---

## 📊 Performance Tips

1. **Use reranking for production** (~10% better quality)
2. **Batch embed large datasets** (50-100 at a time)
3. **Adjust chunk size based on domain**
   - Short answers: 300-500 tokens
   - Long answers: 800-1000 tokens
4. **Monitor database size**
   - Each embedding takes ~1.5KB
   - 1M docs = ~1.5GB storage
5. **Use IVFFlat index** (configured by default)

---

## 🚀 Deployment Checklist

- [ ] PostgreSQL with backups configured
- [ ] All environment variables set
- [ ] Embedding model cached locally
- [ ] Rate limiting configured
- [ ] Monitoring/logging enabled
- [ ] HTTPS enabled
- [ ] Authentication implemented
- [ ] Database indexed properly

---

## 📖 More Resources

- **Full Guide:** [RAG_GUIDE.md](./RAG_GUIDE.md)
- **Examples:** [rag_examples.py](./rag_examples.py)
- **Implementation:** [RAG_IMPLEMENTATION.md](./RAG_IMPLEMENTATION.md)

---

## 💬 Quick Questions

**Q: What's the difference between similarity_score and rerank_score?**
A: `similarity_score` is cosine similarity (0-1). `rerank_score` is cross-encoder ranking (typically -10 to 10, higher is better).

**Q: Why use reranking?**
A: Reranking significantly improves relevance (5-10% better), but adds ~300ms latency.

**Q: What's the ideal chunk size?**
A: Start with 500 tokens. Adjust based on your domain and question complexity.

**Q: Can I use different embedding models?**
A: Yes! Change `EMBEDDING_MODEL` in `.env`. Larger models = better quality but slower.

**Q: How many documents can I store?**
A: Theoretically unlimited. Performance degrades >1M documents without additional optimization.

---

**Ready to go!** Start with `/rag/index` then `/rag/search` 🚀
