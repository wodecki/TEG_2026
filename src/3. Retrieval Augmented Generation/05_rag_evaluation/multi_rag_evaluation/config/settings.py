# Model settings
EXPERT_MODEL = "gpt-5"
EVALUATOR_MODEL = "gpt-4.1"
RAG_MODEL = "gpt-4o-mini"

# Chunking settings (from course modules)
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Retrieval settings
TOP_K = 3

# BM25 specific (for hybrid search)
BM25_K1 = 1.5
BM25_B = 0.75

# Reranking specific
RERANK_TOP_K = 6  # Retrieve more initially
FINAL_TOP_K = 3   # Return top 3 after reranking

# Query expansion
MAX_QUERY_VARIATIONS = 3

# Evaluation questions
EVAL_QUESTIONS = [
    "What did Marie Curie win Nobel Prizes for?",
    "What is Einstein's theory of relativity about?",
    "What are Newton's three laws of motion?",
    "What did Charles Darwin discover?",
    "What was Ada Lovelace's contribution to computing?"
]

# Convert to dict for easy access
def get_config():
    return {
        "EXPERT_MODEL": EXPERT_MODEL,
        "EVALUATOR_MODEL": EVALUATOR_MODEL,
        "RAG_MODEL": RAG_MODEL,
        "CHUNK_SIZE": CHUNK_SIZE,
        "CHUNK_OVERLAP": CHUNK_OVERLAP,
        "TOP_K": TOP_K,
        "BM25_K1": BM25_K1,
        "BM25_B": BM25_B,
        "RERANK_TOP_K": RERANK_TOP_K,
        "FINAL_TOP_K": FINAL_TOP_K,
        "MAX_QUERY_VARIATIONS": MAX_QUERY_VARIATIONS,
        "EVAL_QUESTIONS": EVAL_QUESTIONS
    }