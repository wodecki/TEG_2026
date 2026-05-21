#!/bin/bash
#
# Completely wipe the Neo4j database used by the Scientists GraphRAG demo.
# Deletes every node and relationship, and drops all indexes and constraints,
# leaving an empty database. The Neo4j container itself keeps running.
#
# Usage: ./clean.sh

set -euo pipefail

CONTAINER="neo4j-demo"
NEO4J_USER="${NEO4J_USER:-neo4j}"
NEO4J_PASSWORD="${NEO4J_PASSWORD:-password}"

# Fail fast: the database must be running for this script to do anything.
if ! docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
  echo "ERROR: container '$CONTAINER' is not running. Start it first with ./neo4j.sh" >&2
  exit 1
fi

run_cypher() {
  docker exec -i "$CONTAINER" cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" --format plain "$1"
}

echo "Deleting all nodes and relationships..."
run_cypher "MATCH (n) DETACH DELETE n;"

echo "Dropping all indexes and constraints..."
run_cypher "CALL apoc.schema.assert({}, {});" > /dev/null

REMAINING=$(run_cypher "MATCH (n) RETURN count(n) AS nodes;" | tail -n 1 | tr -d '[:space:]')
if [ "$REMAINING" = "0" ]; then
  echo "Done. Database is empty (0 nodes)."
else
  echo "ERROR: expected 0 nodes after cleanup, found $REMAINING." >&2
  exit 1
fi
