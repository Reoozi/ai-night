#!/usr/bin/env python3
"""
Semantic Search Module for Bakery Ingredient Technical Sheets (RAG)

Challenge Requirements:
- Input: User question (text)
- Processing: Generate embedding with all-MiniLM-L6-v2, search with cosine similarity
- Output: Top 3 results with text fragment and similarity score (2 decimals)
- Database: ChromaDB (local vector database), collection='embeddings'

Constraints:
✓ Model: all-MiniLM-L6-v2 (sentence-transformers)
✓ Dimension: 384
✓ Similarity: Cosine Similarity
✓ Top K: 3 results
✓ Language: Python
✓ No Docker Required!
"""

import sys
import os

# Add app directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from services.embedding_service import EmbeddingService
from services.chroma_store import ChromaVectorStore
from utils.logger import logger
from core.config import settings


class BakeryRAGSearch:
    """RAG Search Engine for Bakery Technical Ingredient Sheets."""
    
    def __init__(self):
        """Initialize embedding model and vector store."""
        try:
            logger.info("Initializing RAG Search Engine...")
            
            # Initialize embedding service (all-MiniLM-L6-v2)
            self.embeddings = EmbeddingService(model_name="all-MiniLM-L6-v2")
            
            # Initialize ChromaDB store (no Docker needed!)
            self.vector_store = ChromaVectorStore()
            
            # Verify constraints
            assert self.embeddings.embedding_dim == 384, "Embedding dimension must be 384"
            assert settings.embedding_model == "all-MiniLM-L6-v2", "Model must be all-MiniLM-L6-v2"
            assert settings.top_k_results == 3, "Top K must be 3"
            
            logger.info("✓ RAG Search Engine initialized successfully")
            logger.info(f"✓ Model: {settings.embedding_model}")
            logger.info(f"✓ Embedding Dimension: {self.embeddings.embedding_dim}")
            logger.info(f"✓ Top K Results: {settings.top_k_results}")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG Search Engine: {str(e)}")
            raise
    
    def search(self, query: str) -> list:
        """
        Search for relevant bakery ingredient technical sheets.
        
        Process:
        1. Generate embedding of the query with all-MiniLM-L6-v2
        2. Search PostgreSQL pgvector with cosine similarity
        3. Return top 3 results
        
        Args:
            query (str): User's natural language question
            
        Returns:
            list: Top 3 results with format:
                {
                    'rank': int,
                    'texte_fragment': str,
                    'similarity_score': float (0-1, rounded to 2 decimals)
                }
        """
        try:
            if not query or not query.strip():
                logger.warning("Empty query provided")
                return []
            
            logger.info(f"Processing query: '{query[:80]}...'")
            
            # Step 1: Generate embedding with constraint model (all-MiniLM-L6-v2)
            query_embedding = self.embeddings.embed(query)
            logger.info(f"✓ Generated embedding (dimension: {len(query_embedding)})")
            
            # Step 2: Search in pgvector with cosine similarity
            results = self.vector_store.search(
                query_embedding=query_embedding,
                top_k=settings.top_k_results  # Constraint: top_k = 3
            )
            
            logger.info(f"✓ Found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            raise
    
    def display_results(self, results: list, query: str = None):
        """
        Display search results in the exact challenge format.
        
        Format:
        Résultat 1
        Texte : "..."
        Score : 0.91
        
        Args:
            results: List of search results
            query: Original query (optional, for logging)
        """
        if not results:
            print("\n❌ No results found.\n")
            return
        
        print("\n" + "="*60)
        if query:
            print(f"📝 Question: {query}\n")
        
        for result in results:
            rank = result.get('rank', 0)
            fragment = result.get('texte_fragment', '')
            score = result.get('similarity_score', 0)
            
            print(f"Résultat {rank}")
            print(f'Texte : "{fragment}"')
            print(f"Score : {score}\n")
        
        print("="*60 + "\n")


def main():
    """
    Main function: Interactive RAG Search for Bakery Ingredients.
    
    Flow:
    1. Initialize RAG Search Engine
    2. Get user question via input()
    3. Generate embedding (all-MiniLM-L6-v2)
    4. Search in PostgreSQL pgvector (cosine similarity)
    5. Display top 3 results
    """
    try:
        print("\n" + "="*60)
        print("🥐 BAKERY INGREDIENT TECHNICAL SHEETS - SEMANTIC SEARCH 🥐")
        print("="*60)
        print("\nChallenge Configuration:")
        print("✓ Model: all-MiniLM-L6-v2 (sentence-transformers)")
        print("✓ Embedding Dimension: 384")
        print("✓ Similarity: Cosine Similarity (pgvector)")
        print("✓ Top K Results: 3")
        print("\n" + "-"*60 + "\n")
        
        # Initialize RAG Search Engine
        logger.info("Starting RAG Bakery Search System...")
        rag_engine = BakeryRAGSearch()
        
        # Get document count
        doc_count = rag_engine.vector_store.get_document_count()
        print(f"📊 Documents in database: {doc_count}\n")
        
        # Interactive search loop
        while True:
            print("-"*60)
            query = input(
                "\n🔍 Enter your question about bakery ingredients "
                "(or 'quit'/'exit' to stop):\n> "
            ).strip()
            
            if query.lower() in ('quit', 'exit', 'q', 'exit()'):
                print("\n👋 Thank you for using the RAG Search. Goodbye!\n")
                break
            
            if not query:
                print("⚠️  Please enter a question.")
                continue
            
            # Execute search
            print("\n⏳ Searching... (all-MiniLM-L6-v2 + cosine similarity)")
            results = rag_engine.search(query)
            
            # Display results
            rag_engine.display_results(results, query)
    
    except KeyboardInterrupt:
        print("\n\n👋 Search interrupted by user.\n")
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"Fatal error in main: {str(e)}")
        print(f"\n❌ ERROR: {str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
