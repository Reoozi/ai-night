#!/usr/bin/env python3
"""
Script de Test pour le Module RAG Boulangerie
Vérifie toutes les exigences du challenge avant l'exécution réelle
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_configuration():
    """Test 1: Vérifier la configuration"""
    print("\n" + "="*60)
    print("TEST 1: Vérification de la Configuration")
    print("="*60)
    
    try:
        from core.config import settings
        
        # Vérifier le modèle d'embedding
        assert settings.embedding_model == "all-MiniLM-L6-v2", \
            f"❌ Modèle incorrect: {settings.embedding_model}"
        print(f"✅ Modèle d'embedding: {settings.embedding_model}")
        
        # Vérifier la dimension
        assert settings.embedding_dimension == 384, \
            f"❌ Dimension incorrecte: {settings.embedding_dimension}"
        print(f"✅ Dimension des embeddings: {settings.embedding_dimension}")
        
        # Vérifier top_k
        assert settings.top_k_results == 3, \
            f"❌ Top K incorrect: {settings.top_k_results}"
        print(f"✅ Top K résultats: {settings.top_k_results}")
        
        # Vérifier la table
        assert settings.embeddings_table == "embeddings", \
            f"❌ Nom de table incorrect: {settings.embeddings_table}"
        print(f"✅ Table database: {settings.embeddings_table}")
        
        # Vérifier les colonnes
        assert settings.fragments_column == "texte_fragment", \
            f"❌ Colonne de fragments incorrecte: {settings.fragments_column}"
        print(f"✅ Colonne fragments: {settings.fragments_column}")
        
        assert settings.vector_column == "vecteur", \
            f"❌ Colonne de vecteur incorrecte: {settings.vector_column}"
        print(f"✅ Colonne vecteur: {settings.vector_column}")
        
        print("\n✅ Configuration: CONFORME")
        return True
        
    except Exception as e:
        print(f"\n❌ Configuration: ÉCHEC - {str(e)}")
        return False


def test_embedding_service():
    """Test 2: Vérifier le service d'embedding"""
    print("\n" + "="*60)
    print("TEST 2: Service d'Embedding")
    print("="*60)
    
    try:
        from services.embedding_service import EmbeddingService
        
        # Initialiser le service
        print("⏳ Chargement du modèle all-MiniLM-L6-v2...")
        embedder = EmbeddingService(model_name="all-MiniLM-L6-v2")
        
        # Vérifier la dimension
        assert embedder.embedding_dim == 384, \
            f"❌ Dimension incorrecte: {embedder.embedding_dim}"
        print(f"✅ Dimension du modèle: {embedder.embedding_dim}")
        
        # Test d'embedding simple
        test_text = "Alpha-amylase : dosage recommandé 0.005% à 0.02%"
        print(f"\n⏳ Test d'embedding sur: '{test_text[:50]}...'")
        
        embedding = embedder.embed(test_text)
        print(f"✅ Embedding généré: shape {embedding.shape}")
        
        # Vérifier la forme
        assert len(embedding) == 384, f"❌ Forme incorrecte: {len(embedding)}"
        print(f"✅ Forme de l'embedding: ({len(embedding)},)")
        
        # Test de similarité cosinus
        embedding2 = embedder.embed("Dosage d'alpha-amylase entre 5 et 20 ppm")
        similarity = embedder.cosine_similarity(embedding, embedding2)
        print(f"✅ Similarité cosinus: {similarity:.4f}")
        
        print("\n✅ Service d'Embedding: OK")
        return True
        
    except Exception as e:
        print(f"\n❌ Service d'Embedding: ÉCHEC - {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_database_connection():
    """Test 3: Vérifier ChromaDB (pas besoin de connexion externe)"""
    print("\n" + "="*60)
    print("TEST 3: ChromaDB Vector Store")
    print("="*60)
    
    try:
        from services.chroma_store import ChromaVectorStore
        from core.config import settings
        
        print(f"⏳ Initialisation de ChromaDB...")
        print(f"   Répertoire de stockage: ./chroma_db")
        
        store = ChromaVectorStore()
        print("✅ ChromaDB initialisé avec succès")
        
        # Vérifier le nombre de documents
        count = store.get_document_count()
        print(f"✅ Collection '{settings.embeddings_table}' : {count} documents")
        
        print("\n✅ ChromaDB: OK (aucun serveur externe nécessaire!)")
        return True
        
    except Exception as e:
        print(f"\n❌ ChromaDB: ÉCHEC - {str(e)}")
        print("\n💡 Solution:")
        print("   ChromaDB doit s'installer automatiquement.")
        print("   Si erreur, exécutez: pip install chromadb")
        return False


def test_chroma_store():
    """Test 4: Vérifier le store ChromaDB"""
    print("\n" + "="*60)
    print("TEST 4: ChromaDB Store")
    print("="*60)
    
    try:
        from services.chroma_store import ChromaVectorStore
        import numpy as np
        
        print("⏳ Initialisation du ChromaDB Store...")
        store = ChromaVectorStore()
        print("✅ ChromaDB Store initialisé")
        
        # Vérifier le nombre de documents
        count = store.get_document_count()
        print(f"✅ Documents dans ChromaDB: {count}")
        
        if count > 0:
            # Test de recherche avec un vecteur aléatoire
            print("\n⏳ Test de recherche vectorielle...")
            random_vector = np.random.rand(384).astype(np.float32)
            
            results = store.search(random_vector, top_k=3)
            print(f"✅ Recherche effectuée: {len(results)} résultats")
            
            if results:
                print("\n📊 Premier résultat (test):")
                first = results[0]
                print(f"   Rang: {first['rank']}")
                print(f"   Texte: {first['texte_fragment'][:80]}...")
                print(f"   Score: {first['similarity_score']}")
        else:
            print("\n⚠️  Aucun document dans ChromaDB")
            print("💡 Utilisez l'endpoint /rag/index pour indexer des documents")
        
        print("\n✅ ChromaDB Store: OK")
        return True
        
    except Exception as e:
        print(f"\n❌ ChromaDB Store: ÉCHEC - {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_rag_search():
    """Test 5: Vérifier le moteur de recherche RAG complet"""
    print("\n" + "="*60)
    print("TEST 5: Moteur de Recherche RAG")
    print("="*60)
    
    try:
        from services.embedding_service import EmbeddingService
        from services.chroma_store import ChromaVectorStore
        from core.config import settings
        
        print("⏳ Initialisation des composants RAG...")
        embedder = EmbeddingService(model_name="all-MiniLM-L6-v2")
        store = ChromaVectorStore()
        print("✅ Composants RAG initialisés")
        
        # Vérifier qu'il y a des documents
        count = store.get_document_count()
        if count == 0:
            print("\n⚠️  Aucun document pour tester la recherche")
            print("   Le système est prêt mais nécessite des données")
            return True
        
        # Test de recherche complète
        test_query = "Améliorant de panification : dosage d'alpha-amylase"
        print(f"\n⏳ Test de recherche: '{test_query}'")
        
        # Étape 1: Générer l'embedding
        query_embedding = embedder.embed(test_query)
        print(f"✅ Embedding de la question généré: {query_embedding.shape}")
        
        # Étape 2: Recherche vectorielle
        results = store.search(query_embedding, top_k=settings.top_k_results)
        print(f"✅ Recherche effectuée: {len(results)} résultats")
        
        # Étape 3: Afficher les résultats
        if results:
            print("\n📊 Résultats de la recherche:")
            print("-" * 60)
            for result in results:
                rank = result['rank']
                text = result['texte_fragment']
                score = result['similarity_score']
                
                print(f"\nRésultat {rank}")
                print(f'Texte : "{text[:100]}..."')
                print(f"Score : {score}")
            print("-" * 60)
        
        print("\n✅ Moteur de Recherche RAG: OK")
        return True
        
    except Exception as e:
        print(f"\n❌ Moteur de Recherche RAG: ÉCHEC - {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Exécuter tous les tests"""
    print("\n" + "="*60)
    print("🧪 TESTS DE CONFORMITÉ - MODULE RAG BOULANGERIE")
    print("="*60)
    print("\nVérification de toutes les exigences du challenge...")
    
    results = []
    
    # Test 1: Configuration
    results.append(("Configuration", test_configuration()))
    
    # Test 2: Embedding Service
    results.append(("Embedding Service", test_embedding_service()))
    
    # Test 3: Database Connection
    db_ok = test_database_connection()
    results.append(("ChromaDB Connection", db_ok))
    
    # Tests suivants uniquement si la DB est OK
    if db_ok:
        results.append(("ChromaDB Store", test_chroma_store()))
        results.append(("RAG Search", test_rag_search()))
    else:
        print("\n⚠️  Tests de ChromaDB ignorés (erreur d'initialisation)")
    
    # Résumé
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*60)
    
    for test_name, passed in results:
        status = "✅ PASSÉ" if passed else "❌ ÉCHOUÉ"
        print(f"{test_name:.<40} {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print("\n" + "="*60)
    print(f"Résultat: {passed}/{total} tests passés")
    print("="*60)
    
    if passed == total:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS!")
        print("✅ Le système est CONFORME aux exigences du challenge")
        print("\n🚀 Pour lancer l'application:")
        print("   python rag_bakery_search.py")
    elif not db_ok:
        print("\n⚠️  PostgreSQL doit être démarré")
        print("\n📝 Instructions:")
        print("   1. Installer Docker Desktop pour Windows")
        print("   2. Lancer: docker-compose -f docker/docker-compose.yml up -d postgres")
        print("   3. Attendre ~10 secondes")
        print("   4. Relancer: python test_rag_system.py")
    else:
        print("\n❌ Certains tests ont échoué")
        print("   Vérifiez les messages d'erreur ci-dessus")
    
    print()
    return 0 if passed == total else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrompus par l'utilisateur\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERREUR FATALE: {str(e)}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
