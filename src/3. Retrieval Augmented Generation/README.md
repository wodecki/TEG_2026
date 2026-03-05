# Retrieval Augmented Generation (RAG)

This repository provides hands-on examples of RAG (Retrieval Augmented Generation), progressing from basic concepts to advanced techniques including knowledge graphs and systematic evaluation.

## 🎯 Learning Objectives

- Master the fundamentals of RAG architecture and implementation
- Compare different vector storage solutions and their trade-offs
- Explore advanced retrieval techniques (hybrid search, reranking, query expansion)
- Learn systematic evaluation using the RAGAS framework
- Understand knowledge graph-based RAG with Neo4j
- Build production-ready RAG systems with proper evaluation

## 📚 Module Structure

### [01_basic_rag/](01_basic_rag/) - RAG Fundamentals
- Minimal RAG implementation with in-memory storage
- Text chunking strategies and their impact on retrieval
- Core RAG pipeline: Load → Embed → Store → Retrieve → Generate

### [02_vector_stores/](02_vector_stores/) - Storage Solutions
- **InMemory**: Fast development and prototyping
- **ChromaDB**: Persistent storage with metadata support
- **FAISS**: High-performance production-scale search

### [03_document_loading/](03_document_loading/) - Data Ingestion
- Text file processing and preprocessing
- PDF extraction and handling
- Web scraping and content extraction

### [04_advanced_retrieval/](04_advanced_retrieval/) - Enhanced Techniques
- Metadata filtering for precise retrieval
- Hybrid search combining BM25 + vector similarity
- Query expansion with multiple query generation
- Reranking with cross-encoder models

### [05_rag_evaluation/](05_rag_evaluation/) - Systematic Assessment
- RAGAS framework for objective evaluation
- Independent ground truth generation with GPT-5
- Multi-system comparison framework
- Production-ready evaluation pipelines

### [06_GraphRAG/](06_GraphRAG/) - Knowledge Graph RAG
- Neo4j integration with Docker
- LLM-powered knowledge graph extraction
- Structured queries impossible with traditional RAG
- GraphRAG vs Naive RAG comparison

### [07_Your_Project_TalentMatch/](07_Your_Project_TalentMatch/) - Capstone Project
- Independent implementation project
- Real-world application of learned concepts

## 🚀 Quick Start

### Prerequisites
- **Python 3.9+** (tested with 3.11+)
- **[uv](https://github.com/astral-sh/uv)** - Fast Python package manager
- **OpenAI API key** - For LLM and embedding models
- **Docker Desktop** - Required for GraphRAG module (Neo4j)

### Installation

1. **Install uv** (if not already installed):
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # or with pipx
   pipx install uv
   ```

2. **Clone and setup**:
   ```bash
   cd "3. Retrieval Augmented Generation"
   uv venv
   uv sync
   ```

3. **Configure environment**:
   ```bash
   # Create .env file with your OpenAI API key
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```

### Running Examples

**Start with the basics:**
```bash
# Minimal RAG implementation
uv run python "01_basic_rag/1. minimal_rag.py"

# Compare chunking strategies
uv run python "01_basic_rag/2. minimal_rag_wtih_chunking.py"
```

**Explore vector stores:**
```bash
# Try different storage options
uv run python "02_vector_stores/1_in_memory.py"
uv run python "02_vector_stores/2_chroma_basic.py"
uv run python "02_vector_stores/3_faiss_intro.py"
```

**Advanced retrieval techniques:**
```bash
# Test metadata filtering
uv run python "04_advanced_retrieval/1_metadata_filtering.py"

# Experience hybrid search
uv run python "04_advanced_retrieval/2_hybrid_search.py"
```

**RAG evaluation:**
```bash
# Simple RAGAS evaluation
uv run python "05_rag_evaluation/1. RAGAS_Naive_RAG.py"

# Multi-system comparison
cd 05_rag_evaluation/multi_rag_evaluation
uv run python main.py
```

**GraphRAG with Neo4j:**
```bash
# Start Neo4j database
./06_GraphRAG/start_session.sh

# Generate and analyze CV data
uv run python "06_GraphRAG/1_generate_data.py"
uv run python "06_GraphRAG/2_data_to_knowledge_graph.py"

# Compare GraphRAG vs Naive RAG
uv run python "06_GraphRAG/5_compare_systems.py"

# Browse knowledge graph at http://localhost:7474 (neo4j/password123)
```

## 🛠️ Technical Stack

### Core Technologies
- **LangChain Ecosystem**: RAG framework and integrations
- **OpenAI**: GPT models (4o, 4o-mini) and embeddings
- **Vector Stores**: ChromaDB, FAISS, InMemory
- **Graph Database**: Neo4j with Docker
- **Evaluation**: RAGAS framework

### Key Dependencies
```toml
langchain = "0.3.24"              # Core RAG framework
langchain-openai = "0.3.11"       # OpenAI integration
langchain-chroma = "0.2.3"        # ChromaDB support
langchain-neo4j = "0.5.0"         # GraphRAG support
chromadb = "0.6.3"                # Persistent vector store
faiss-cpu = "1.12.0"              # High-performance search
ragas = "0.3.5"                   # RAG evaluation
neo4j = "5.28.2"                  # Graph database driver
```

## 📊 What You'll Learn

### RAG Implementation Patterns
- Document loading and preprocessing strategies
- Text chunking optimization for different use cases
- Vector embedding and storage trade-offs
- Retrieval techniques and ranking methods
- Prompt engineering for RAG systems

### Production Considerations
- Performance optimization with FAISS
- Persistent storage with ChromaDB
- Error handling and fallback strategies
- Cost optimization with model selection
- Systematic evaluation and monitoring

### Advanced Techniques
- Hybrid search combining keyword + semantic similarity
- Query expansion and reformulation
- Document reranking with cross-encoders
- Knowledge graph integration for structured queries
- Multi-system evaluation frameworks

## 🎓 Learning Path

1. **Start with Module 1**: Understand core RAG concepts
2. **Progress through Modules 2-4**: Build technical depth
3. **Master Module 5**: Learn proper evaluation techniques
4. **Explore Module 6**: Advanced knowledge graph approaches
5. **Apply in Module 7**: Independent project implementation

Each module includes detailed README files with learning objectives, key concepts, and troubleshooting guides.

## 🔧 Development Tips

### Common Commands
```bash
# Install new dependencies
uv add package_name

# Run specific module
uv run python "module/script.py"

# Check Neo4j status (GraphRAG)
uv run python "06_GraphRAG/0_setup.py" --check
```

### Environment Variables
Required in `.env` file:
```bash
OPENAI_API_KEY=your_openai_api_key
```

### Troubleshooting
- **Import errors**: Run `uv sync` to install dependencies
- **API errors**: Verify `OPENAI_API_KEY` in `.env` file
- **Neo4j issues**: Ensure Docker Desktop is running
- **Memory issues**: Reduce chunk sizes or batch sizes

## 📈 Performance Benchmarks

### Vector Store Comparison
| Store | Startup (First) | Startup (Cached) | Search Speed | Best For |
|-------|----------------|------------------|--------------|----------|
| InMemory | ~30s | ~30s | Fast | Development |
| ChromaDB | ~30s | ~2s | Good | General Use |
| FAISS | ~30s | ~1s | Excellent | Production |

### RAG System Evaluation Results
Latest RAGAS evaluation comparing 5 RAG approaches:

| System | Context Precision | Context Recall | Faithfulness | Answer Relevancy |
|--------|-------------------|----------------|--------------|------------------|
| Naive RAG | 0.700 | **0.634** | 0.743 | 0.881 |
| Query Expansion | 0.700 | 0.501 | 0.775 | **0.948** |
| Reranking | 0.567 | 0.434 | **0.767** | 0.935 |

## 🤝 Contributing

This is an educational repository. For improvements or bug fixes:
1. Fork the repository
2. Create a feature branch
3. Test your changes across multiple modules
4. Submit a pull request with clear description

## 📄 License

Educational use. Please respect OpenAI API terms and Neo4j licensing when using this code.

## 🔗 Related Resources

- [LangChain Documentation](https://python.langchain.com/)
- [RAGAS Evaluation Framework](https://docs.ragas.io/)
- [Neo4j Graph Database](https://neo4j.com/docs/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)