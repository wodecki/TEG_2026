#!/bin/bash

# GraphRAG Start Session Script
# =============================
# Start your GraphRAG session from persisted data

echo "🚀 Starting GraphRAG Session"
echo "============================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running"
    echo "Please start Docker Desktop and try again"
    exit 1
fi

# Start Neo4j
echo "▶️  Starting Neo4j..."
docker-compose up -d

# Wait for Neo4j to be ready
echo "⏳ Waiting for Neo4j to be ready..."
sleep 10

# Check connection and show status
echo "🔍 Checking system status..."
uv run python 0_setup.py --check

echo ""
echo "✅ GraphRAG session started!"
echo ""
echo "🎯 What you can do now:"
echo "• Query the graph: uv run python 3_query_knowledge_graph.py"
echo "• Open Neo4j Browser: http://localhost:7474"
echo "• Check status anytime: uv run python 0_setup.py --check"
echo "• End session: ./end_session.sh"
echo ""
echo "🔑 Neo4j Browser credentials:"
echo "   Username: neo4j"
echo "   Password: password123"