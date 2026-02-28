# PostgreSQL + pgvector Setup Guide

## 🐳 Option 1: Docker (Recommended for Development)

### Quick Start

```bash
cd docker/
docker-compose up -d
```

This starts PostgreSQL 15 with pgvector extension pre-installed.

### Verify Setup

```bash
# Check container is running
docker ps | grep postgres

# Connect to database (password: password)
psql -h localhost -U postgres -d rag_db
```

Once connected, verify pgvector:

```sql
-- Check pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
\dx

-- Check vector type
SELECT * FROM pg_type WHERE typname = 'vector';
```

### Stop Services

```bash
docker-compose down
```

### Reset Database

```bash
docker-compose down -v
docker-compose up -d
```

---

## 🖥️ Option 2: Manual PostgreSQL Installation

### Windows

#### 1. Install PostgreSQL

- Download from: https://www.postgresql.org/download/windows/
- Run installer and note the password you set
- Recommended: PostgreSQL 14+ with pgAdmin

#### 2. Install pgvector

```bash
# Install from source
git clone https://github.com/pgvector/pgvector.git
cd pgvector
```

Or use pre-built release from: https://github.com/pgvector/pgvector/releases

#### 3. Create Database

```bash
# Using psql
psql -U postgres

# In psql prompt:
CREATE DATABASE rag_db;
\c rag_db
CREATE EXTENSION pgvector;
\dx
```

#### 4. Verify Installation

```bash
psql -U postgres -d rag_db -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

---

### macOS

```bash
# Install PostgreSQL (using Homebrew)
brew install postgresql@15

# Start PostgreSQL
brew services start postgresql@15

# Install pgvector
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make PG_CONFIG=/usr/local/opt/postgresql@15/bin/pg_config
make install PG_CONFIG=/usr/local/opt/postgresql@15/bin/pg_config

# Create database
createdb -U postgres rag_db
psql -U postgres -d rag_db -c "CREATE EXTENSION pgvector;"
```

---

### Linux (Ubuntu/Debian)

```bash
# Install PostgreSQL
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib postgresql-dev

# Install pgvector from source
sudo apt-get install build-essential git
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install

# Create database
sudo -u postgres createdb rag_db
sudo -u postgres psql -d rag_db -c "CREATE EXTENSION pgvector;"

# Verify
sudo -u postgres psql -d rag_db -c "\dx"
```

---

## 🔧 Configuration

### Connection String

Update your `.env`:

```env
PGVECTOR_HOST=localhost
PGVECTOR_PORT=5432
PGVECTOR_DB=rag_db
PGVECTOR_USER=postgres
PGVECTOR_PASSWORD=password
```

### Connection String Format

```
postgresql://user:password@host:port/database
```

Example:

```
postgresql://postgres:password@localhost:5432/rag_db
```

---

## 🧪 Testing the Connection

### Python Connection Test

```python
import psycopg2
from pgvector.psycopg2 import register_vector

connection_string = "postgresql://postgres:password@localhost:5432/rag_db"

try:
    conn = psycopg2.connect(connection_string)
    register_vector(conn)

    cursor = conn.cursor()

    # Test 1: Check pgvector extension
    cursor.execute("SELECT extname FROM pg_extension WHERE extname = 'pgvector';")
    print("pgvector extension:", cursor.fetchone())

    # Test 2: Create test table with vector
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_vectors (
            id SERIAL PRIMARY KEY,
            content TEXT,
            embedding vector(384)
        );
    """)

    # Test 3: Insert test vector
    cursor.execute(
        "INSERT INTO test_vectors (content, embedding) VALUES (%s, %s)",
        ("test", [0.1] * 384)
    )

    # Test 4: Query test
    cursor.execute("SELECT * FROM test_vectors;")
    print("Test record:", cursor.fetchone())

    conn.commit()
    cursor.close()
    conn.close()

    print("✓ Connection successful!")

except Exception as e:
    print(f"✗ Connection failed: {e}")
```

### Direct psql Test

```bash
# Connect
psql -h localhost -U postgres -d rag_db

# In psql:
\dx pgvector

-- Test vector type
SELECT ARRAY[0.1, 0.2, 0.3]::vector;

-- Test similarity
SELECT (ARRAY[0.1, 0.2]::vector) <=> ARRAY[0.15, 0.25]::vector;
```

---

## 📦 Troubleshooting

### Issue: "could not load library"

```
ERROR: could not load library "/usr/lib/postgresql/15/lib/vector.so"
```

**Solution:**

- Rebuild pgvector for your PostgreSQL version
- Check PostgreSQL version: `psql --version`
- Rebuild: `make clean && make && make install`

---

### Issue: "Extension pgvector does not exist"

```
ERROR: extension "pgvector" does not exist
```

**Solution:**

- Reinstall pgvector
- Check installation: `ls /usr/lib/postgresql/15/lib/vector.so`
- If not found, follow installation steps above

---

### Issue: "Connection refused"

```
psycopg2.OperationalError: could not connect to server: Connection refused
```

**Solution:**

- Verify PostgreSQL is running
- Check host/port in connection string
- Check firewall settings
- For Docker:
  ```bash
  docker ps | grep postgres
  docker logs postgres_vectordb
  ```

---

### Issue: "FATAL: password authentication failed"

```
FATAL: password authentication failed for user "postgres"
```

**Solution:**

- Check password in `.env`
- Reset password:
  ```bash
  sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'password';"
  ```

---

### Issue: Low disk space

```
ERROR: could not extend file "pg_tblspc/..." no space left on device
```

**Solution:**

- Clean old backups
- Clear vector table: `TRUNCATE documents;`
- Or add more disk space

---

## 🔄 Backup & Restore

### Backup Database

```bash
# Full backup
pg_dump rag_db > rag_db_backup.sql

# Custom format (recommended, compresses)
pg_dump -Fc rag_db > rag_db_backup.dump

# With Docker
docker exec postgres_vectordb pg_dump -U postgres rag_db > backup.sql
```

### Restore Database

```bash
# From SQL file
psql rag_db < rag_db_backup.sql

# From custom format
pg_restore -d rag_db rag_db_backup.dump

# With Docker
docker exec -i postgres_vectordb psql -U postgres rag_db < backup.sql
```

---

## 📊 Performance Optimization

### Index Optimization

```sql
-- Check index status
SELECT indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE relname = 'documents';

-- Reindex if needed
REINDEX INDEX documents_embedding_idx;
```

### Database Maintenance

```sql
-- Analyze table
ANALYZE documents;

-- Vacuum (cleanup)
VACUUM documents;

-- Full maintenance (slow, do during downtime)
VACUUM FULL ANALYZE documents;
```

### Vector Dimension Optimization

```sql
-- Check memory usage
SELECT
    COUNT(*) as docs,
    pg_size_pretty(pg_total_relation_size('documents')) as size,
    pg_size_pretty(avg_relation_size) as avg_size
FROM documents;
```

---

## 🔐 Security

### Change Default Password (Production)

```bash
# Connect as postgres user
sudo -u postgres psql

# Change password
ALTER USER postgres PASSWORD 'your_secure_password';
\q
```

### Create Limited User (Production)

```sql
-- Create read-only user
CREATE USER rag_reader PASSWORD 'reader_password';
GRANT CONNECT ON DATABASE rag_db TO rag_reader;
GRANT USAGE ON SCHEMA public TO rag_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO rag_reader;

-- Create read-write user
CREATE USER rag_writer PASSWORD 'writer_password';
GRANT CONNECT ON DATABASE rag_db TO rag_writer;
GRANT USAGE ON SCHEMA public TO rag_writer;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO rag_writer;
```

### SSL/TLS (Production)

```bash
# Generate certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout server.key -out server.crt

# Configure PostgreSQL
# Add to postgresql.conf:
# ssl = on
# ssl_cert_file = '/path/to/server.crt'
# ssl_key_file = '/path/to/server.key'
```

---

## 🚀 Production Checklist

- [ ] PostgreSQL 13+ installed
- [ ] pgvector extension installed
- [ ] rag_db database created
- [ ] User authentication configured
- [ ] Regular backups scheduled
- [ ] SSL/TLS enabled
- [ ] Connection pooling configured
- [ ] Monitoring set up
- [ ] Resource limits defined
- [ ] Documentation reviewed

---

## 📚 Resources

- PostgreSQL Docs: https://www.postgresql.org/docs/
- pgvector GitHub: https://github.com/pgvector/pgvector
- psycopg2 Docs: https://www.psycopg.org/psycopg2/docs/

---

## ✓ Verification Checklist

After setup, verify:

```
✓ Docker running (if using Docker)
✓ psql can connect
✓ pgvector extension loaded
✓ test_vectors table created
✓ Vector operations work
✓ .env configured correctly
✓ Python can connect
✓ RAG service initializes
```

---

**PostgreSQL + pgvector is now ready!** 🎉
