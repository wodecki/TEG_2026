#!/bin/bash

docker rm -f neo4j-demo 2>/dev/null

docker run -d \
  --name neo4j-demo \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  -e NEO4J_PLUGINS='["apoc"]' \
  neo4j:latest

echo "Neo4j is starting. Open http://localhost:7474 in ~30 seconds (login: neo4j / password)."
