# 🥐 GUIDE D'EXÉCUTION - Challenge RAG Boulangerie

## 🚀 5 Étapes Rapides pour Tester

### **Étape 1: Vérifier les Prérequis**

```bash
# Docker + PostgreSQL avec pgvector doivent tourner
docker ps | grep postgres

# Si rien n'apparaît, lancez:
cd docker
docker-compose up -d
cd ..
```

### **Étape 2: Installer les Dépendances**

```bash
pip install -r requirements.txt
```

**Temps estimé:** 2-3 minutes (télécharge sentence-transformers)

### **Étape 3: Vérifier la Base de Données**

```bash
# Connectez-vous à PostgreSQL
psql -U postgres -h localhost -d rag_db

# Vérifiez la table 'embeddings'
\dt embeddings;
SELECT COUNT(*) FROM embeddings;

# Quittez
\q
```

**Attendu:**
- Table `embeddings` avec colonnes: `id, id_document, texte_fragment, vecteur`
- Plusieurs documents déjà indexés

### **Étape 4: Lancer le Module de Recherche**

```bash
# De la racine du projet
python rag_bakery_search.py
```

### **Étape 5: Tester une Recherche**

```
🔍 Enter your question about bakery ingredients:
> Quelles sont les quantités recommandées d'alpha-amylase et xylanase ?
```

**Résultat attendu:**
```
Résultat 1
Texte : "L'alpha-amylase est recommandée à..."
Score : 0.91

Résultat 2
Texte : "La xylanase améliore..."
Score : 0.87

Résultat 3
Texte : "..."
Score : 0.82
```

---

## 📋 Vérification des Contraintes

### ✅ Vérifier le Modèle d'Embedding

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")
dim = model.get_sentence_embedding_dimension()
print(f"Dimension: {dim}")  # Doit afficher: 384
```

### ✅ Tester la Similarité Cosine

```sql
-- Dans PostgreSQL
SELECT 1 - (vecteur <=> '[0.1, 0.2, ...]'::vector) as similarity
FROM embeddings
ORDER BY similarity DESC
LIMIT 3;
```

### ✅ Valider les Contraintes au Runtime

```bash
# Le script rag_bakery_search.py affiche à l'initialisation:
# ✓ Model: all-MiniLM-L6-v2
# ✓ Embedding Dimension: 384
# ✓ Top K Results: 3
```

---

## 🐛 Troubleshooting

### **Erreur: "Failed to connect to database"**

**Solution:**
```bash
# 1. Vérifiez que Docker tourne
docker ps

# 2. Vérifiez PostgreSQL
docker logs postgres_vectordb

# 3. Relancez si nécessaire
docker-compose down
docker-compose up -d
```

### **Erreur: "Model not found"**

**Solution:**
```bash
# Télécharge all-MiniLM-L6-v2 automatiquement la première fois
# Assurez-vous d'avoir internet

# Force le téléchargement:
python -c "from sentence_transformers import SentenceTransformer; \
           SentenceTransformer('all-MiniLM-L6-v2')"
```

### **Erreur: "Table embeddings not found"**

**Solution:**
```sql
-- Créez la table manuellement:
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    id_document INT,
    texte_fragment TEXT NOT NULL,
    vecteur vector(384),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX embeddings_vector_idx 
ON embeddings USING ivfflat (vecteur vector_cosine_ops)
WITH (lists = 100);
```

### **Erreur: "Dimension mismatch"**

**Solution:**
```bash
# Assurez-vous que:
# 1. Le modèle est all-MiniLM-L6-v2 (384 dim)
# 2. Pas de messages d'erreur lors du téléchargement
# 3. Les vecteurs stockés en DB ont bien 384 dimensions
```

---

## 📊 Métriques & Performance

### Temps d'Exécution

| Opération | Temps |
|-----------|-------|
| Initialisation | ~2s (première fois) |
| Génération embedding | ~100ms |
| Recherche (top 3) | ~50ms |
| **Total par question** | ~150ms |

### Taille des Données

| Métrique | Valeur |
|----------|--------|
| Dimension embedding | 384 |
| Taille par vecteur | ~1.5 KB |
| Index IVFFLAT | +20% stockage |

---

## 🔄 Flux Complet du Challenge

```
┌─────────────────────────────────────┐
│   UTILISATEUR ENTRE UNE QUESTION    │
│   "Quantités alpha-amylase ?"       │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   EMBEDDING SERVICE                 │
│   - Model: all-MiniLM-L6-v2         │
│   - Output: vector(384)             │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   PGVECTOR STORE                    │
│   - Search: vecteur <=> embedding   │
│   - Similarity: 1 - distance        │
│   - Limit: top 3                    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   RÉSULTATS TRIÉS                   │
│   - Score 1: 0.91                   │
│   - Score 2: 0.87                   │
│   - Score 3: 0.82                   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   AFFICHAGE FORMATÉ                 │
│   Résultat 1                        │
│   Texte : "..."                     │
│   Score : 0.91                      │
└─────────────────────────────────────┘
```

---

## 📝 Exemple Complet de Test

### Input

```
Question: "Améliorant de panification : quelles sont les quantités recommandées 
d'alpha-amylase, xylanase et d'Acide ascorbique ?"
```

### Process

```
1. Embedding: question → vector(384)
2. Search: SELECT * FROM embeddings WHERE similarity TOP 3
3. Results: 
   - id=45, score=0.918
   - id=67, score=0.873
   - id=23, score=0.821
```

### Output

```
Résultat 1
Texte : "L'alpha-amylase est un enzyme recommandée à 500-1000 unités/kg pour 
améliorer le rendu de panification..."
Score : 0.92

Résultat 2
Texte : "La xylanase augmente la rétention d'eau et la structure du gluten. 
Dosage recommandé : 200-500 unités/kg..."
Score : 0.87

Résultat 3
Texte : "L'acide ascorbique (Vitamine C) renforce les liaisons disulfures du gluten.
Dosage : 50-200 mg/kg..."
Score : 0.82
```

---

## ✅ Checklist Avant Soumission

- [ ] PostgreSQL + pgvector tourne
- [ ] Table `embeddings` existe et est remplie
- [ ] `python rag_bakery_search.py` s'exécute sans erreur
- [ ] Input: la question s'entre avec `input()`
- [ ] Processing: embedding all-MiniLM-L6-v2 (384 dim)
- [ ] Search: utilise pgvector cosine similarity
- [ ] Top K: retourne exactement 3 résultats
- [ ] Output: format "Résultat N, Texte, Score"
- [ ] Scores: arrondi à 2 décimales
- [ ] Gestion erreurs: DB connection, searc exceptions
- [ ] Documentation: code commenté et clean
- [ ] Requirements: toutes les dépendances listées

---

## 🎯 Points Clés du Challenge

1. **Modèle obligatoire:** `all-MiniLM-L6-v2` (pas d'autres options)
2. **Dimension fixe:** 384 (validée à l'init)
3. **Similarité:** cosine uniquement (opérateur pgvector `<=>`)
4. **Résultats:** top 3 seulement (pas plus, pas moins)
5. **Format:** Résultat N / Texte / Score (0-1, 2 décimales)
6. **Language:** Python uniquement
7. **Input:** via `input()` interactive
8. **Output:** affichage formaté, pas de fichier

---

## 📞 Support

Pour les erreurs PostgreSQL:
```bash
psql -U postgres -h localhost
\d embeddings
SELECT COUNT(*) FROM embeddings;
```

Pour les erreurs embedding:
```bash
python -c "from services.embedding_service import EmbeddingService; \
           e = EmbeddingService(); \
           print(f'Dim: {e.embedding_dim}')"
```

Pour tracer la recherche:
```bash
# Activer les logs detaillés
export LOG_LEVEL=DEBUG
python rag_bakery_search.py
```

---

**Prêt à soumettre! 🚀**
