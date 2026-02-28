#!/bin/bash
# RAG System Complete Startup Script

echo "================================================"
echo "🚀 RAG Semantic Search System - Startup Guide"
echo "================================================"
echo ""

# Check PostgreSQL
echo "1️⃣  Checking PostgreSQL with pgvector..."
docker ps | grep -q "postgres_vectordb"
if [ $? -eq 0 ]; then
    echo "✅ PostgreSQL is running"
else
    echo "❌ PostgreSQL not running. Starting..."
    cd docker
    docker-compose up -d
    cd ..
    echo "⏳ Waiting for PostgreSQL to be ready..."
    sleep 10
fi

echo ""
echo "2️⃣  Checking Python dependencies..."
python -c "import pgvector" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ All dependencies installed"
else
    echo "❌ Installing dependencies..."
    pip install -r requirements.txt
fi

echo ""
echo "3️⃣  Starting Backend Server..."
echo "📍 Backend will run on: http://127.0.0.1:8000"
echo "📍 API docs will be at: http://127.0.0.1:8000/docs"
echo ""
echo "Starting in new terminal window..."
python app/main.py &
BACKEND_PID=$!

# Give backend time to start
sleep 3

echo ""
echo "4️⃣  Starting Frontend..."
cd frontend
echo "📍 Frontend will run on: http://localhost:3000"
echo ""
npm run dev

# Cleanup on exit
trap "kill $BACKEND_PID" EXIT
