#!/usr/bin/env python
"""
Sample script demonstrating RAG system usage.
Run this to test the RAG pipeline end-to-end.
"""
import sys
import os
import asyncio
import json

# Add app directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from services.rag_service import rag_service


async def example_1_basic_indexing():
    """Example 1: Basic document indexing."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Document Indexing")
    print("="*60)
    
    documents = [
        {
            "content": """University Leave Policy:
            Employees are entitled to:
            - 20 days annual leave per year
            - 10 days sick leave per year

            - 5 days unpaid leave (at manager discretion)
            
            Leave request process:
            1. Submit request through HR portal
            2. Manager approval (within 2 working days)
            3. HR confirmation
            4. Update calendar
            """,
            "title": "Leave Policy",
            "source": "hr_manual.pdf",
            "category": "Human Resources"
        },
        {
            "content": """Salary Payment Information:
            - Base salary paid on the last working day of each month
            - Bonuses paid quarterly in March, June, September, December
            - Overtime calculated at 1.5x hourly rate
            - Tax deductions as per local regulations
            - Direct deposit to registered bank account
            """,
            "title": "Salary Information",
            "source": "finance_guide.pdf",
            "category": "Finance"
        },
        {
            "content": """Performance Review Process:
            - Annual reviews conducted in January
            - Quarterly check-ins with managers
            - 360-degree feedback from colleagues
            - Rating scale: Needs Improvement, Meets Expectations, Exceeds Expectations
            - Salary adjustments based on performance ratings
            """,
            "title": "Performance Reviews",
            "source": "performance_guide.pdf",
            "category": "Human Resources"
        }
    ]
    
    result = await rag_service.index_documents(documents)
    print(f"\nIndexing Result:")
    print(json.dumps(result, indent=2))
    
    stats = rag_service.get_stats()
    print(f"\nSystem Statistics:")
    print(json.dumps({
        "total_documents": stats["total_documents"],
        "embedding_model": stats["embedding_model"],
        "embedding_dimension": stats["embedding_dimension"]
    }, indent=2))


async def example_2_semantic_search():
    """Example 2: Semantic search without reranking."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Semantic Search (Without Reranking)")
    print("="*60)
    
    query = "How many days of leave do I get per year?"
    print(f"\nQuery: '{query}'")
    
    result = await rag_service.retrieve(query, top_k=5, use_reranker=False)
    
    print(f"\nFound {result['results_count']} results (cosine similarity):")
    for i, doc in enumerate(result['results'], 1):
        print(f"\n{i}. Similarity Score: {doc['similarity_score']:.4f}")
        print(f"   Title: {doc['metadata'].get('title', 'N/A')}")
        print(f"   Content: {doc['content'][:150]}...")
        print(f"   Category: {doc['metadata'].get('category', 'N/A')}")


async def example_3_with_reranker():
    """Example 3: Semantic search with reranking."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Semantic Search (With Reranking)")
    print("="*60)
    
    query = "When is my salary paid?"
    print(f"\nQuery: '{query}'")
    
    result = await rag_service.retrieve(query, top_k=3, use_reranker=True)
    
    print(f"\nFound {result['results_count']} results (after reranking):")
    for i, doc in enumerate(result['results'], 1):
        print(f"\n{i}. Rerank Score: {doc.get('rerank_score', 'N/A'):.4f}")
        print(f"   Similarity Score: {doc['similarity_score']:.4f}")
        print(f"   Title: {doc['metadata'].get('title', 'N/A')}")
        print(f"   Content: {doc['content'][:150]}...")


async def example_4_multiple_queries():
    """Example 4: Multiple queries to compare reranking."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Comparing Multiple Queries")
    print("="*60)
    
    queries = [
        "How often are performance reviews conducted?",
        "What's the overtime payment rate?",
        "Can I take unpaid leave?"
    ]
    
    for query in queries:
        print(f"\n{'─'*60}")
        print(f"Query: '{query}'")
        
        # Without reranking
        result_no_rerank = await rag_service.retrieve(
            query, top_k=3, use_reranker=False
        )
        
        # With reranking
        result_with_rerank = await rag_service.retrieve(
            query, top_k=3, use_reranker=True
        )
        
        print(f"\nTop result without reranking:")
        if result_no_rerank['results']:
            doc = result_no_rerank['results'][0]
            print(f"  Score: {doc['similarity_score']:.4f}")
            print(f"  Title: {doc['metadata'].get('title', 'N/A')}")
        
        print(f"\nTop result with reranking:")
        if result_with_rerank['results']:
            doc = result_with_rerank['results'][0]
            print(f"  Score: {doc.get('rerank_score', doc['similarity_score']):.4f}")
            print(f"  Title: {doc['metadata'].get('title', 'N/A')}")


async def main():
    """Run all examples."""
    try:
        # Example 1: Index documents
        await example_1_basic_indexing()
        
        # Example 2: Search without reranking
        await example_2_semantic_search()
        
        # Example 3: Search with reranking
        await example_3_with_reranker()
        
        # Example 4: Multiple queries
        await example_4_multiple_queries()
        
        print("\n" + "="*60)
        print("All examples completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\nError running examples: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("Starting RAG System Examples...")
    print("Make sure PostgreSQL with pgvector is running!")
    asyncio.run(main())
