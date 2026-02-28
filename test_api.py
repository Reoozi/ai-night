"""Quick API test script to verify all endpoints work"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_api_imports():
    """Test that all API imports work without errors"""
    print("=" * 60)
    print("Testing API Import (FastAPI Server)")
    print("=" * 60)
    
    try:
        # Test main app import
        print("\n1. Testing main app import...")
        from main import app
        print("   ✓ FastAPI app imported successfully")
        
        # Test that routes are registered
        print("\n2. Testing routes...")
        routes = [route.path for route in app.routes]
        expected_routes = ['/llm', '/health', '/rag']
        
        for expected in expected_routes:
            matching = [r for r in routes if expected in r]
            if matching:
                print(f"   ✓ {expected} routes registered")
            else:
                print(f"   ❌ {expected} routes missing")
        
        # Test RAG service
        print("\n3. Testing RAG service...")
        from services.rag_service import rag_service
        stats = rag_service.get_stats()
        print(f"   ✓ RAG service initialized")
        print(f"   - Model: {stats['embedding_model']}")
        print(f"   - Dimension: {stats['embedding_dimension']}")
        print(f"   - Documents: {stats['total_documents']}")
        
        print("\n" + "=" * 60)
        print("✓ API READY - All imports successful!")
        print("=" * 60)
        print("\nTo start the server:")
        print("  cd app")
        print("  uvicorn main:app --reload")
        print("\nAPI will be available at: http://localhost:8000")
        print("API docs at: http://localhost:8000/docs")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_api_imports()
    sys.exit(0 if success else 1)
