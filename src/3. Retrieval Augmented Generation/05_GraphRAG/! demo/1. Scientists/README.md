# GraphRAG Demo — Scientists

A minimal GraphRAG demo. An LLM reads five scientist
biographies from `scientists_bios/`, extracts a **knowledge graph** from them,
stores it in **Neo4j**, and then answers natural-language questions by
generating Cypher queries.

## What the demo shows

1. An LLM turns plain text into typed **nodes** and **relationships**.
2. The result is a graph you can **see and explore** in the Neo4j Browser.
3. Questions are answered by translating them to **Cypher**, not by vector search —
   so counting, filtering and multi-hop questions are exact.

## Files

| File | Purpose |
|------|---------|
| `neo4j.sh` | Start a local Neo4j database in a Docker container |
| `scientists_bios/` | Five plain-text scientist biographies — the demo's input data |
| `generate_graph.py` | Read the biographies, extract the knowledge graph, store it in Neo4j |
| `query_graph.py` | Ask natural-language questions — GraphRAG generates and runs Cypher |

## Prerequisites

- **Docker Desktop** running
- **Python 3.10+** with `uv`
- An **OpenAI API key**

---

## Step 1 — Start Neo4j

```bash
chmod +x neo4j.sh
./neo4j.sh
```

Wait about 30 seconds for the database to come up.

## Step 2 — Open the Neo4j Browser (web GUI)

Open **http://localhost:7474** in a browser and connect with:

| Field | Value |
|-------|-------|
| Connect URL | `bolt://localhost:7687` |
| Username | `neo4j` |
| Password | `password` |

The database is empty. Confirm it in the query bar at the top:

```cypher
MATCH (n) RETURN count(n)
```

It returns `0`.

## Step 3 — Install dependencies

```bash
uv add langchain-openai langchain-experimental langchain-neo4j
```

Both scripts read `OPENAI_API_KEY` from the `.env` file in the repository root
(`load_dotenv(override=True)`), so no `export` is needed.

## Step 4 — Build the knowledge graph

```bash
uv run python generate_graph.py
```

The LLM extracts nodes and relationships from each biography and writes them to Neo4j.

## Step 5 — Explore the graph in the Neo4j Browser

Back in the browser (http://localhost:7474), run:

```cypher
MATCH (n) RETURN n
```

You will see the whole graph: `Scientist`, `Field`, `Country`, `Institution`,
`Discovery` and `Award` nodes connected by relationships.

Interesting queries:

```cypher
// each scientist and what they discovered
MATCH (s:Scientist)-[:DISCOVERED]->(d:Discovery) RETURN s, d
```

```cypher
// scientists grouped by the country they were born in
MATCH (s:Scientist)-[:BORN_IN]->(c:Country) RETURN s, c
```

```cypher
// who won an award
MATCH (s:Scientist)-[:WON]->(a:Award) RETURN s, a
```

**Point to make:** Isaac Newton is mentioned in *two* biographies — his own and
Albert Einstein's. In the graph he is a **single node**: the knowledge graph
links information across documents, which plain text chunks cannot do.

## Step 6 — Ask questions (GraphRAG inference)

```bash
uv run python query_graph.py
```

For each question this prints the **Cypher query the LLM generated** and the
final answer. Example questions used:

- Which scientists were born in England?
- How many scientists won a Nobel Prize?
- What did Marie Curie discover?
- Which scientists worked at Cambridge?

---

## How it works

1. `generate_graph.py` reads every `.txt` file in `scientists_bios/` and sends each
   biography to `LLMGraphTransformer`. Using GPT-4o, it extracts typed nodes and
   relationships following a fixed schema.
2. The extracted graph is written to Neo4j with `add_graph_documents`.
3. `query_graph.py` uses `GraphCypherQAChain`: it reads the graph schema,
   translates a natural-language question into a Cypher query, runs it against
   Neo4j, and turns the result into a sentence. A custom prompt tells the LLM to
   match entity names case-insensitively and partially (`CONTAINS`), so small
   naming differences between the question and the graph do not cause misses.

## The schema

**Nodes:** `Scientist`, `Field`, `Country`, `Institution`, `Discovery`, `Award`

**Relationships:** `WORKED_IN`, `BORN_IN`, `WORKED_AT`, `DISCOVERED`, `WON`, `INFLUENCED`

## Cleanup

```bash
docker stop neo4j-demo && docker rm neo4j-demo
```
