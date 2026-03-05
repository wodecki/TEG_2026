# GraphRAG vs Naive RAG: CV Knowledge Graph Comparison

A comprehensive demonstration of **GraphRAG vs Naive RAG** using realistic PDF CVs and LLM-powered knowledge graph extraction. This project showcases how knowledge graphs enable structured queries that are impossible with traditional vector-based RAG systems.

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** with `uv` package manager
- **Docker Desktop** (for Neo4j database)
- **OpenAI API Key** (set in `.env` file)

### One-Command Demo
```bash
# Complete end-to-end comparison
uv run python 5_compare_systems.py
```

### Step-by-Step Workflow
```bash
# 1. Initial setup and validation
uv run python 0_setup.py

# 2. Start Neo4j database
./start_session.sh

# 3. Generate 30 realistic CV PDFs
uv run python 1_generate_data.py

# 4. Extract knowledge graph from CVs using LLMGraphTransformer
uv run python 2_data_to_knowledge_graph.py

# 5. Run complete comparison
uv run python 5_compare_systems.py
```

## 🎯 Problem Addressed

Traditional RAG systems struggle with structured queries requiring:

| Query Type | Example | Traditional RAG Issue |
|------------|---------|---------------------|
| **Counting** | "How many Python developers?" | ❌ Estimates from text chunks |
| **Filtering** | "Find people with Docker AND Kubernetes" | ❌ Limited to semantic similarity |
| **Aggregation** | "Average years of experience?" | ❌ Cannot calculate across entities |
| **Sorting** | "Top 3 most experienced developers" | ❌ No structured ranking |
| **Multi-hop** | "People who attended same university" | ❌ Cannot traverse relationships |

## 🏗️ Architecture

### Knowledge Graph Schema
**Auto-extracted from PDF CVs using LLMGraphTransformer:**

```
Nodes:
├── Person (id, name, location, bio)
├── Skill (id, category)
├── Company (id, industry, location)
├── University (id, location, type)
└── Certification (id, provider, field)

Relationships:
├── (Person)-[HAS_SKILL]->(Skill)
├── (Person)-[WORKED_AT]->(Company)
├── (Person)-[STUDIED_AT]->(University)
├── (Person)-[EARNED]->(Certification)
└── (Person)-[MENTIONS]->(Person)
```

### System Components
- **PDF Processing**: Realistic CV generation with reportlab
- **Knowledge Extraction**: LangChain LLMGraphTransformer
- **Graph Database**: Neo4j with Docker
- **GraphRAG**: LangChain GraphCypherQAChain with custom prompts
- **Naive RAG**: ChromaDB vector search baseline
- **Evaluation**: GPT-5 ground truth generation

## 📊 Example Results

### Query: "How many people have Python programming skills?"

**GraphRAG (✅ Accurate):**
```cypher
MATCH (p:Person)-[:HAS_SKILL]->(s:Skill)
WHERE toLower(s.id) = toLower("Python")
RETURN count(p) AS pythonProgrammers
```
*Result: **7 people** (exact count)*

**Naive RAG (❌ Incomplete):**
*Result: "Based on context, only **Amanda Smith** is mentioned" (missed 6 people)*

### Query: "List people with both React and Node.js skills"

**GraphRAG (✅ Complete):**
*Result: **4 people** - Christine Rodriguez, Joseph Fuller, Krystal Castillo, William Bonilla*

**Naive RAG (❌ Limited):**
*Result: **1 person** - Christine Rodriguez (missed 3 people)*

## 📁 Project Structure

```
06_GraphRAG/
├── 0_setup.py                 # Environment validation
├── 1_generate_data.py          # Synthetic PDF CV generation
├── 2_data_to_knowledge_graph.py  # LLM graph extraction
├── 3_query_knowledge_graph.py  # GraphRAG implementation
├── 4_naive_rag_cv.py          # Naive RAG baseline
├── 5_compare_systems.py       # System comparison
├── docker-compose.yml         # Neo4j setup
├── start_session.sh           # Neo4j management
├── utils/                     # Utility files
│   ├── generate_ground_truth.py  # GPT-5 ground truth
│   ├── test_questions.json    # Evaluation questions
│   └── config.toml           # Configuration
├── data/programmers/          # Generated CV PDFs
└── results/                   # Comparison results
    ├── ground_truth_answers.json
    └── comparison_report.md
```

## 🔧 Technical Stack

- **Language**: Python 3.11+
- **Package Manager**: uv
- **LLM**: OpenAI GPT-4o (queries), GPT-5 (ground truth)
- **Graph Database**: Neo4j 5.x with Docker
- **Vector Store**: ChromaDB (baseline comparison)
- **Frameworks**: LangChain, LangChain Experimental
- **Document Processing**: Unstructured, ReportLab

## 🎓 Key Learnings

1. **GraphRAG excels** at structured queries requiring precise relationships
2. **LLMGraphTransformer** enables real-world PDF-to-knowledge-graph workflows
3. **Custom Cypher prompts** solve case sensitivity and result interpretation issues
4. **GPT-5 ground truth** provides unbiased evaluation
5. **Hybrid approaches** can combine both strengths for optimal results


## 🔍 Advanced Usage

### Browse Knowledge Graph
Neo4j Browser: http://localhost:7474 (neo4j/password123)

### Individual Components
```bash
# Test GraphRAG only
uv run python 3_query_knowledge_graph.py

# Test Naive RAG only
uv run python 4_naive_rag_cv.py

# Generate ground truth only
uv run python utils/generate_ground_truth.py
```

## 🤝 Real-World Applications

This approach applies to any domain with:
- **Structured relationships** between entities
- **Precise counting/filtering** requirements
- **Multi-hop reasoning** needs
- **Complex business queries**

Examples: Staffing, inventory management, medical records, financial risk analysis.
