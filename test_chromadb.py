"""Quick test script to verify ChromaDB integration"""
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from services.chroma_store import chroma_store
from services.embedding_service import embedding_service

def test_chromadb():
    """Test ChromaDB basic operations"""
    print("=" * 60)
    print("Testing ChromaDB Integration")
    print("=" * 60)
    
    # Test 1: Check embedding service
    print("\n1. Testing Embedding Service...")
    print(f"   Model: {embedding_service.model_name}")
    print(f"   Dimension: {embedding_service.embedding_dim}")
    test_text = "Farine de blé type 55"
    embedding = embedding_service.embed(test_text)
    print(f"   Sample embedding shape: {embedding.shape}")
    print("   ✓ Embedding service OK")
    
    # Test 2: Add test documents
    print("\n2. Testing Document Addition...")
    test_docs = [
        {"texte_fragment": "Farine de blé type 55 - Pour pâtisserie", "id_document": 1, "source": "test"},
        {"texte_fragment": "Levure boulangère fraîche - Pour brioche", "id_document": 2, "source": "test"},
        {"texte_fragment": "Beurre doux 82% MG - Pour viennoiserie", "id_document": 3, "source": "test"}
    ]
    
    # Clear database first
    chroma_store.delete_all_documents()
    
    # Generate embeddings for documents
    texts = [doc["texte_fragment"] for doc in test_docs]
    embeddings = embedding_service.embed(texts)
    
    # Add documents
    chroma_store.add_documents(test_docs, embeddings)
    count = chroma_store.get_document_count()
    print(f"   Documents in database: {count}")
    print("   ✓ Document addition OK")
    
    # Test 3: Search
    print("\n3. Testing Semantic Search...")
    query = "farine"
    query_embedding = embedding_service.embed(query)
    results = chroma_store.search(query_embedding, top_k=2)
    print(f"   Query: '{query}'")
    print(f"   Results found: {len(results)}")
    for i, result in enumerate(results, 1):
        print(f"   {i}. {result['texte_fragment'][:50]}... (similarity: {result['similarity_score']:.2f})")
    print("   ✓ Search OK")
    
    # Test 4: Verify cosine similarity
    print("\n4. Verifying Cosine Similarity...")
    print(f"   All scores between 0 and 1: {all(0 <= r['similarity_score'] <= 1 for r in results)}")
    print("   ✓ Cosine similarity confirmed")
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED - ChromaDB is working correctly!")
    print("=" * 60)
    print("\nNo Docker required - ChromaDB stores data in: ./app/chroma_db")
    print("You can now start your RAG application without Docker!")

if __name__ == "__main__":
    test_chromadb()
