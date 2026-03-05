# Module 5: RAG Evaluation with RAGAS

This module demonstrates how to evaluate RAG (Retrieval Augmented Generation) systems using the RAGAS (Retrieval Augmented Generation Assessment) framework. It showcases both simple single-file evaluation and a comprehensive multi-system comparison framework.

## Learning Objectives

- Understand RAGAS evaluation metrics and methodology
- Learn proper ground truth generation for RAG evaluation
- Compare different RAG retrieval strategies objectively
- Apply software engineering best practices to evaluation systems
- Transition from prototype to production-ready evaluation code

## Module Structure

```
05_rag_evaluation/
├── 1. RAGAS_Naive_RAG.py          # Simple single-file RAGAS evaluation
├── data/                          # Scientist biographies dataset
│   └── scientists_bios/
├── multi_rag_evaluation/          # Professional multi-RAG comparison system
│   ├── rag_systems/              # Modular RAG implementations
│   ├── evaluation/               # RAGAS evaluation engine
│   ├── config/                   # Configuration management
│   ├── results/                  # Generated evaluation results
│   └── main.py                   # Main evaluation orchestrator
└── README.md                     # This file
```

## Part 1: Single-File RAGAS Evaluation

### File: `1. RAGAS_Naive_RAG.py` (124 lines)

A minimal, educational implementation demonstrating:

- **Independent Ground Truth Generation**: Uses GPT-5 with complete document context
- **Basic RAG Pipeline**: Simple vector similarity search with LangChain
- **Core RAGAS Metrics**: Context Precision, Context Recall, Faithfulness, Answer Relevancy, Factual Correctness
- **No Fallbacks**: Fails fast on missing requirements (following best practices)

**Key Features:**
- Single file for easy understanding
- Expert LLM (GPT-5) generates ground truth with full document access
- RAG system (GPT-4o-mini) uses chunked retrieval for realistic comparison
- Course module patterns: `as_retriever()`, `RunnablePassthrough`, `ChatPromptTemplate`

**Running:**
```bash
uv run python "1. RAGAS_Naive_RAG.py"
```

## Part 2: Multi-RAG Evaluation System

### Directory: `multi_rag_evaluation/` (980+ lines total)

A professional, extensible evaluation framework comparing 5 RAG approaches:

#### RAG Systems Evaluated

1. **Naive RAG** - Basic vector similarity search (baseline)
2. **Metadata Filtering RAG** - Enhanced retrieval using document metadata
3. **Hybrid Search RAG** - Combines BM25 keyword + vector search
4. **Query Expansion RAG** - LLM-generated query variations
5. **Reranking RAG** - Post-retrieval document re-ranking

#### Architecture Components

**`rag_systems/`** - Modular RAG implementations
- `base_rag.py` - Abstract base class ensuring consistency
- `naive_rag.py` - Baseline implementation
- `metadata_filtering_rag.py` - Field-based filtering
- `hybrid_search_rag.py` - BM25 + vector fusion
- `query_expansion_rag.py` - Multi-query retrieval
- `reranking_rag.py` - Cross-encoder re-ranking

**`evaluation/`** - RAGAS evaluation engine
- `evaluator.py` - Multi-system comparison logic
- `ground_truth.py` - Expert answer generation

**`config/`** - Configuration management
- `settings.py` - Centralized parameters

**`main.py`** - Orchestration script with error handling

#### Latest Evaluation Results

| System | Context Precision | Context Recall | Faithfulness | Answer Relevancy | Factual Correctness |
|--------|-------------------|----------------|--------------|------------------|-------------------|
| **Naive RAG** | 0.700 | **0.634** | 0.743 | 0.881 | 0.400 |
| **Metadata Filtering** | 0.500 | 0.287 | 0.613 | 0.884 | 0.406 |
| **Hybrid Search** | 0.700 | 0.494 | 0.738 | 0.918 | 0.404 |
| **Query Expansion** | 0.700 | 0.501 | 0.775 | **0.948** | 0.396 |
| **Reranking** | 0.567 | 0.434 | **0.767** | 0.935 | **0.436** |

**Key Insights:**
- **Query Expansion** achieves highest answer relevancy (0.948)
- **Reranking** shows best faithfulness (0.767) and factual correctness (0.436)
- **Naive RAG** surprisingly leads in context recall (0.634)
- **Metadata Filtering** struggles with limited biographical metadata
- Advanced techniques don't always outperform simpler approaches

## Installation & Setup

### Prerequisites
```bash
# Create and activate virtual environment
uv venv
source ./venv/bin/activate

# Install dependencies
uv sync

# Set OpenAI API key
export OPENAI_API_KEY="your-api-key"
# or create .env file with OPENAI_API_KEY=your-api-key
```

### Required Packages
- `ragas` - RAG evaluation framework
- `langchain` ecosystem - RAG components
- `openai` - LLM and embeddings
- `rank-bm25` - Hybrid search (optional)
- `sentence-transformers` - Re-ranking (optional)

## Usage

### Simple Evaluation
```bash
# Run single-file RAGAS evaluation
uv run python "1. RAGAS_Naive_RAG.py"
```

### Multi-System Comparison
```bash
# Run comprehensive evaluation
cd multi_rag_evaluation
uv run python main.py

# Results saved to: results/comparison_metrics.csv
```

## Understanding RAGAS Metrics

### Core Metrics Explained

- **Context Precision**: What fraction of retrieved contexts are relevant?
  - *High = less noise in retrieval*

- **Context Recall**: What fraction of relevant contexts were retrieved?
  - *High = comprehensive information gathering*

- **Faithfulness**: Is the answer grounded in retrieved context?
  - *High = reduced hallucination*

- **Answer Relevancy**: How well does the answer address the question?
  - *High = better user experience*

- **Factual Correctness**: How accurate is the answer vs. ground truth?
  - *High = reliable information*

### Ground Truth Generation

**Critical Design Decision**: Use independent expert LLM with complete document access:

```python
# ✅ CORRECT: Independent ground truth
expert_llm = ChatOpenAI(model="gpt-5")  # Stronger model
full_context = load_complete_documents()  # All information
ground_truth = expert_llm.invoke(f"Context: {full_context}\nQuestion: {q}")

# ❌ WRONG: Circular dependency
ground_truth = same_rag_system.query(question)  # Self-evaluation bias
```

## Educational Progression

### 1. **Simple Start** (`1. RAGAS_Naive_RAG.py`)
- Single file, ~124 lines
- Focus on core concepts
- Direct execution pattern

### 2. **Professional Refactor** (`multi_rag_evaluation/`)
- Modular architecture, 980+ lines
- Abstract base classes
- Configuration management
- Error handling
- Extensible design

### 3. **Software Engineering Lessons**
- **Separation of Concerns**: RAG logic ≠ evaluation logic
- **Abstract Base Classes**: Ensure consistent interfaces
- **Configuration**: Externalize parameters
- **Error Handling**: Graceful degradation
- **Modularity**: Easy to add new RAG systems

## Extensions & Experiments

### Adding New RAG Systems
1. Inherit from `BaseRAG`
2. Implement `build()` and `name` property
3. Add to `main.py` initialization
4. Run evaluation

### Custom Metrics
- Extend RAGAS with domain-specific metrics
- Add business logic evaluation
- Include cost/latency analysis

### Advanced Comparisons
- Statistical significance testing
- Confidence intervals
- Cross-validation across question sets

## Research Applications

This framework enables systematic RAG research:

- **Retrieval Strategy Analysis**: Which approaches work best for different question types?
- **Parameter Optimization**: Chunk size, overlap, k values
- **Model Comparisons**: Different LLMs and embedding models
- **Domain Adaptation**: Performance across different knowledge domains

## Common Issues & Solutions

### Missing Dependencies
```bash
# If BM25 missing:
uv add rank-bm25

# If sentence-transformers missing:
uv add sentence-transformers
```

### Model Access Issues
- Ensure valid OpenAI API key
- Check model availability (GPT-5, GPT-4.1)
- Adjust temperature settings per model requirements

### Memory Issues
- Reduce chunk size or batch size
- Use streaming for large datasets
- Monitor token usage

## Best Practices

1. **Independent Ground Truth**: Never use the same system for both generation and evaluation
2. **Fair Comparison**: Same questions, same evaluation conditions
3. **Multiple Metrics**: No single metric tells the full story
4. **Error Handling**: Graceful degradation when components fail
5. **Reproducibility**: Fixed seeds, documented parameters
6. **Cost Awareness**: Monitor API usage, especially with GPT-5

## Further Reading

- [RAGAS Documentation](https://docs.ragas.io/)
- [LangChain RAG Tutorial](https://python.langchain.com/docs/tutorials/rag/)
- [Retrieval Evaluation Best Practices](https://arxiv.org/abs/2308.07107)
