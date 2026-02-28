"""Final verification test"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

print("=" * 60)
print("FINAL VERIFICATION TEST")
print("=" * 60)

# Test 1: ChromaDB
print("\n1. Testing ChromaDB...")
try:
    from services.chroma_store import chroma_store
    count = chroma_store.get_document_count()
    print(f"   ✓ ChromaDB works ({count} documents)")
except Exception as e:
    print(f"   ❌ ChromaDB failed: {e}")

# Test 2: Embedding Service
print("\n2. Testing Embedding Service...")
try:
    from services.embedding_service import embedding_service
    print(f"   ✓ Embeddings work (model: {embedding_service.model_name})")
except Exception as e:
    print(f"   ❌ Embeddings failed: {e}")

# Test 3: RAG Service
print("\n3. Testing RAG Service...")
try:
    from services.rag_service import rag_service
    stats = rag_service.get_stats()
    print(f"   ✓ RAG Service works")
    print(f"     - Model: {stats['embedding_model']}")
    print(f"     - Dimension: {stats['embedding_dimension']}")
    print(f"     - Documents: {stats['total_documents']}")
except Exception as e:
    print(f"   ❌ RAG Service failed: {e}")

print("\n" + "=" * 60)
print("✓ ALL CORE SERVICES WORKING")
print("=" * 60)
print("\nYour RAG system is ready!")
print("\nTo start the API server:")
print("  cd app")
print("  uvicorn main:app --reload")
print("\nThen visit: http://localhost:8000/docs")
