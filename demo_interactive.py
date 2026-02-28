#!/usr/bin/env python3
"""
Interactive Demo: Bakery RAG Search System
Test your system with sample bakery ingredient queries
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from services.rag_service import rag_service
from services.embedding_service import embedding_service
from services.chroma_store import chroma_store
import asyncio
from typing import List, Dict

# Sample bakery ingredient data for testing
SAMPLE_DOCUMENTS = [
    {
        "texte_fragment": "Farine de blé type 55 : Protéines 10-11%, idéale pour la pâtisserie et les viennoiseries. Absorption d'eau: 58-60%.",
        "id_document": 1,
        "source": "fiche_farine_t55"
    },
    {
        "texte_fragment": "Alpha-amylase : Enzyme recommandée à 0.005% à 0.02% du poids de farine. Améliore le volume et la texture du pain.",
        "id_document": 2,
        "source": "fiche_enzymes"
    },
    {
        "texte_fragment": "Levure boulangère fraîche : Dosage recommandé 2-3% du poids de farine. Conservation 4°C maximum 15 jours.",
        "id_document": 3,
        "source": "fiche_levure"
    },
    {
        "texte_fragment": "Xylanase : Améliore l'extensibilité de la pâte. Dosage: 5-15 ppm. Particulièrement efficace pour les pâtes complètes.",
        "id_document": 4,
        "source": "fiche_enzymes"
    },
    {
        "texte_fragment": "Acide ascorbique (vitamine C) : Agent oxydant, dosage 5-20 ppm. Renforce le gluten et améliore la tenue de la pâte.",
        "id_document": 5,
        "source": "fiche_additifs"
    },
    {
        "texte_fragment": "Beurre 82% MG : Pour viennoiserie fine. Température de travail: 16-18°C. Dosage croissants: 25-30% du poids de farine.",
        "id_document": 6,
        "source": "fiche_matieres_grasses"
    },
    {
        "texte_fragment": "Sel : Dosage standard 1.8-2% du poids de farine. Ralentit la fermentation, renforce le gluten.",
        "id_document": 7,
        "source": "fiche_ingredients_base"
    },
    {
        "texte_fragment": "Gluten vital : Renfort pour farines faibles. Dosage 0.5-2%. Augmente l'élasticité et la capacité de rétention gazeuse.",
        "id_document": 8,
        "source": "fiche_additifs"
    }
]

# Sample test queries
SAMPLE_QUERIES = [
    "Quelles sont les quantités recommandées d'alpha-amylase ?",
    "Quel est le dosage de levure pour du pain ?",
    "Comment utiliser la xylanase ?",
    "Quelle farine pour la pâtisserie ?",
    "Dosage de vitamine C dans le pain ?",
]


async def setup_sample_data():
    """Add sample documents to ChromaDB"""
    print("\n" + "="*60)
    print("🔧 SETUP: Adding sample bakery ingredient data...")
    print("="*60)
    
    # Clear existing data
    chroma_store.delete_all_documents()
    print("✓ Cleared existing data")
    
    # Generate embeddings
    texts = [doc["texte_fragment"] for doc in SAMPLE_DOCUMENTS]
    embeddings = embedding_service.embed(texts)
    print(f"✓ Generated {len(embeddings)} embeddings")
    
    # Store in ChromaDB
    chroma_store.add_documents(SAMPLE_DOCUMENTS, embeddings)
    count = chroma_store.get_document_count()
    print(f"✓ Stored {count} documents in ChromaDB")
    
    print("\n📊 Sample documents:")
    for i, doc in enumerate(SAMPLE_DOCUMENTS[:3], 1):
        preview = doc["texte_fragment"][:60] + "..." if len(doc["texte_fragment"]) > 60 else doc["texte_fragment"]
        print(f"  {i}. {preview}")
    print(f"  ... and {len(SAMPLE_DOCUMENTS) - 3} more\n")


async def test_search(query: str):
    """Test semantic search with a query"""
    print("\n" + "="*60)
    print(f"📝 QUERY: {query}")
    print("="*60)
    
    # Perform search
    result = await rag_service.retrieve(
        query=query,
        top_k=3,
        use_reranker=False
    )
    
    # Display results
    if result['status'] == 'success' and result['results']:
        print(f"\n✅ Found {result['results_count']} results:\n")
        
        for res in result['results']:
            print(f"{'─'*60}")
            print(f"Rang {res['rank']}")
            print(f"Texte : \"{res['texte_fragment']}\"")
            print(f"Score : {res['similarity_score']:.2f}")
            print()
    else:
        print("\n❌ No results found")


async def interactive_mode():
    """Interactive search mode"""
    print("\n" + "="*60)
    print("🎯 INTERACTIVE MODE")
    print("="*60)
    print("Type your question (or 'exit' to quit, 'sample' for examples)")
    
    while True:
        print("\n📝", end=" ")
        query = input("Question: ").strip()
        
        if not query:
            continue
        
        if query.lower() in ['exit', 'quit', 'q']:
            print("\n👋 Au revoir!")
            break
        
        if query.lower() == 'sample':
            print("\nSample queries:")
            for i, q in enumerate(SAMPLE_QUERIES, 1):
                print(f"  {i}. {q}")
            continue
        
        await test_search(query)


async def run_demo():
    """Run the complete demo"""
    print("\n")
    print("🥐"*30)
    print("\n  BAKERY RAG SEARCH SYSTEM - INTERACTIVE DEMO")
    print("\n" + "🥐"*30)
    
   # Check if data exists
    count = chroma_store.get_document_count()
    
    if count == 0:
        print("\n⚠️  No data in database. Loading sample data...")
        await setup_sample_data()
    else:
        print(f"\n✓ Database has {count} documents")
        print("\nOptions:")
        print("  1. Use existing data")
        print("  2. Reset with fresh sample data")
        choice = input("\nYour choice (1 or 2): ").strip()
        
        if choice == '2':
            await setup_sample_data()
    
    # Run a few sample searches
    print("\n" + "🧪"*60)
    print("\n  DEMO: Running sample searches...")
    print("\n" + "🧪"*60)
    
    for i, query in enumerate(SAMPLE_QUERIES[:3], 1):
        print(f"\n--- Sample {i}/3 ---")
        await test_search(query)
        await asyncio.sleep(0.5)  # Brief pause for readability
    
    # Interactive mode
    print("\n" + "="*60)
    choice = input("\nWant to try your own questions? (y/n): ").strip().lower()
    
    if choice in ['y', 'yes', 'oui']:
        await interactive_mode()
    
    # Show statistics
    print("\n" + "="*60)
    print("📊 SYSTEM STATISTICS")
    print("="*60)
    stats = rag_service.get_stats()
    print(f"Total documents : {stats['total_documents']}")
    print(f"Embedding model : {stats['embedding_model']}")
    print(f"Vector dimension: {stats['embedding_dimension']}")
    print(f"Reranker model  : {stats['reranker_model']}")
    
    print("\n" + "="*60)
    print("✅ DEMO COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("  • Add your own documents via the API")
    print("  • Integrate into your application")
    print("  • Start the API server: cd app && uvicorn main:app --reload")
    print("\n")


if __name__ == "__main__":
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
