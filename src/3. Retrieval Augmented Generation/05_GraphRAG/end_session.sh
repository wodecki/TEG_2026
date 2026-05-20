#!/bin/bash

# GraphRAG End Session Script
# ===========================
# Save your work and stop Neo4j cleanly

echo "💾 Ending GraphRAG Session"
echo "=========================="

# Check if Neo4j is running
if ! docker ps | grep -q neo4j; then
    echo "ℹ️  Neo4j is not running"
    echo "Nothing to stop"
    exit 0
fi

# Show current status
echo "📊 Current session data:"
echo "• Neo4j container: $(docker ps | grep neo4j | wc -l | tr -d ' ') running"
echo "• GraphRAG network active"

echo ""
echo "⏹️  Stopping Neo4j..."
docker-compose down

echo ""
echo "✅ Session ended successfully!"
echo ""
echo "📋 What happened:"
echo "• Neo4j stopped cleanly"
echo "• All your data is preserved in Docker volumes"
echo "• Database will be exactly as you left it"
echo ""
echo "🚀 To continue working:"
echo "• Run: ./start_session.sh"
echo "• Or: docker-compose up -d"
echo ""
echo "💡 Your data persists automatically - no manual saving needed!"