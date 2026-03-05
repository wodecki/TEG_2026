# Module 4: Advanced Retrieval Techniques

## Learning Objectives
- Master metadata filtering and contextual retrieval
- Implement hybrid search combining semantic and keyword search
- Optimize retrieval with re-ranking and query expansion
- Build multi-step retrieval pipelines
- Understand retrieval evaluation and optimization

## Prerequisites
- Completed Module 3 (Document Loading)
- Understanding of vector stores and embeddings
- Familiarity with document chunking strategies
- OpenAI API key configured

## Scripts in This Module

### 1. `1_metadata_filtering.py` - Contextual Retrieval
Advanced metadata-based filtering techniques:
- Enhanced metadata extraction from documents (scientist names, fields, birth years)
- Field-specific filtering (physics, mathematics, chemistry)
- Quality-based filtering (document completeness)
- Contextual query analysis for automatic filter selection
- Performance comparison showing filtering effectiveness

**Key learning:** How metadata enhances retrieval precision and relevance

### 2. `2_hybrid_search.py` - Semantic + Keyword Search
Combining multiple search approaches:
- Vector search with OpenAI embeddings
- BM25 keyword search implementation
- TF-IDF search for additional keyword matching
- Reciprocal Rank Fusion (RRF) and weighted score fusion
- Adaptive search strategy based on query analysis
- Performance benchmarking across query types

**Key learning:** When and how to combine different search methodologies

### 3. `3_query_expansion.py` - Enhanced Query Processing
Improving queries before retrieval:
- Simple synonym and concept expansion
- LLM-based query expansion with multiple strategies
- Multi-perspective query generation (historical, technical, impact)
- Context-aware expansion using domain knowledge
- Query expansion pipeline with effectiveness analysis

**Key learning:** Pre-processing techniques that improve retrieval quality

### 4. `4_reranking.py` - Post-Retrieval Optimization
Refining retrieval results:
- Cross-encoder re-ranking with multiple models (MS-MARCO, QNLI)
- LLM-based relevance scoring
- Diversity re-ranking for result variety
- Ensemble re-ranking combining multiple methods
- Performance vs. quality trade-off analysis

**Key learning:** Post-processing techniques for optimal result quality

**Note:** Only 4 scripts are implemented in this module. Evaluation has been moved to a future dedicated module for comprehensive coverage.

## Key Concepts

- **Metadata Filtering**: Using document properties to constrain search space
- **Hybrid Search**: Combining semantic and lexical search methods
- **Query Expansion**: Enriching queries with related terms and concepts
- **Re-ranking**: Post-processing to improve result relevance
- **Retrieval Evaluation**: Systematic measurement of system performance
- **Multi-stage Retrieval**: Pipeline approaches for complex queries

## Retrieval Strategy Comparison

| Approach | Precision | Recall | Speed | Complexity | Best For |
|----------|-----------|--------|-------|------------|----------|
| **Basic Vector Search** | 🟡 Medium | 🟢 High | 🟢 Fast | 🟢 Simple | General queries |
| **Metadata Filtered** | 🟢 High | 🟡 Medium | 🟢 Fast | 🟡 Medium | Contextual search |
| **Hybrid Search** | 🟢 High | 🟢 High | 🟡 Medium | 🔴 Complex | Diverse queries |
| **Query Expanded** | 🟢 High | 🟢 High | 🟡 Medium | 🟡 Medium | Concept search |
| **Re-ranked** | 🟢 Highest | 🟡 Medium | 🔴 Slow | 🔴 Complex | Quality-critical |

## Running the Code

```bash
# Metadata filtering techniques
uv run python "04_advanced_retrieval/1_metadata_filtering.py"

# Hybrid search implementation
uv run python "04_advanced_retrieval/2_hybrid_search.py"

# Query expansion strategies
uv run python "04_advanced_retrieval/3_query_expansion.py"

# Re-ranking and optimization
uv run python "04_advanced_retrieval/4_reranking.py"
```

## Expected Behavior

**1_metadata_filtering.py:**
- Extracts rich metadata from scientist biographies
- Demonstrates field-specific filtering (physics vs. mathematics)
- Shows contextual query analysis for automatic filtering
- Compares filtered vs. unfiltered retrieval results

**2_hybrid_search.py:**
- Implements vector search, BM25, and TF-IDF search
- Demonstrates query analysis and adaptive routing
- Shows Reciprocal Rank Fusion and weighted score combination
- Benchmarks performance across different query types

**3_query_expansion.py:**
- Shows synonym expansion and concept mapping
- Demonstrates LLM-based query expansion with multiple strategies
- Implements multi-perspective query generation
- Compares expansion effectiveness across query types

**4_reranking.py:**
- Loads and compares multiple cross-encoder models
- Demonstrates LLM-based relevance scoring
- Shows ensemble re-ranking combining multiple methods
- Benchmarks performance vs. quality trade-offs

## Dependencies Added

This module adds advanced retrieval dependencies:
- **rank-bm25**: BM25 keyword search implementation
- **sentence-transformers**: Cross-encoder models for re-ranking (MS-MARCO, QNLI)
- **scikit-learn**: TF-IDF vectorization and cosine similarity
- **numpy**: Numerical operations for score fusion and normalization

## Advanced Retrieval Pipeline

```
Query Input
    ↓
Query Analysis & Expansion
    ↓
Metadata Filter Application
    ↓
Parallel Search:
├── Semantic (Vector)
├── Keyword (BM25)
└── Structured (Metadata)
    ↓
Score Fusion & Initial Ranking
    ↓
Re-ranking (Cross-encoder/LLM)
    ↓
Post-processing:
├── Deduplication
├── Diversity
└── Result Formatting
    ↓
Final Results
```

## Best Practices by Technique

**Metadata Filtering:**
- Design rich metadata schemas upfront
- Index metadata fields for fast filtering
- Use hierarchical categories when appropriate
- Consider filter combinations carefully

**Hybrid Search:**
- Understand query intent for method selection
- Tune score fusion weights empirically
- Implement fallback strategies
- Monitor performance vs. complexity trade-offs

**Query Expansion:**
- Generate diverse expansion strategies
- Use domain-specific expansion terms
- Limit expansion to avoid noise
- Validate expanded queries make sense

**Re-ranking:**
- Use re-ranking for top-k results only (demonstrated with k*2 initial retrieval)
- Consider computational cost vs. benefit (benchmarked in script)
- Load multiple cross-encoder models for comparison
- Implement ensemble methods for robust re-ranking

## Common Issues

- **Filter over-specification**: Too restrictive metadata filters (scripts show fallback strategies)
- **Score fusion complexity**: Combining different scoring methods (demonstrated with normalization)
- **Query expansion noise**: Irrelevant expansion terms (LLM-based expansion helps)
- **Re-ranking latency**: Slow cross-encoder models (benchmarked in performance analysis)
- **Model loading time**: Cross-encoder models require initial download and loading
