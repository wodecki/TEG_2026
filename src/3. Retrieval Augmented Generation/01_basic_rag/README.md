# Module 1: Basic RAG

## Learning Objectives
- Understand the core RAG (Retrieval Augmented Generation) architecture
- Implement a minimal RAG system using in-memory vector storage
- Learn the importance of text chunking for improved retrieval
- Compare different chunking strategies and their impact on results

## Prerequisites
- Basic understanding of LLMs and embeddings (covered in previous course)
- OpenAI API key configured in environment

## Scripts in This Module

### 1. `1. minimal_rag.py` - Simplest RAG Implementation
A bare-bones RAG system that demonstrates the core concept without complexity:
- Loads documents from the scientists_bios dataset
- Creates embeddings using OpenAI
- Stores everything in an in-memory vector store
- Implements basic retrieval and generation

**Key learning:** Understanding the RAG pipeline: Load → Embed → Store → Retrieve → Generate

### 2. `2. minimal_rag_wtih_chunking.py` - RAG with Text Splitting
Enhanced RAG system that introduces document chunking:
- Splits long documents into smaller, focused chunks
- Compares different chunk sizes (500, 1000, 2000 characters)
- Retrieves multiple relevant chunks per query
- Demonstrates how chunking improves retrieval accuracy

**Key learning:** Why chunking matters and how to optimize chunk size for your use case

## Key Concepts

- **RAG Pipeline**: The core flow of document loading, embedding, storing, retrieving, and generating responses
- **Vector Store**: A database that stores document embeddings for similarity search
- **Retrieval**: Finding the most relevant documents/chunks based on query similarity
- **Text Chunking**: Breaking large documents into smaller, more focused segments
- **Chunk Size vs Overlap**: Balancing context completeness with retrieval precision

## Running the Code

Make sure you're in the project root directory:

```bash
# Run minimal RAG example
uv run python "1. minimal_rag.py"

# Run chunking comparison
uv run python "2. minimal_rag_wtih_chunking.py"
```

## Expected Output

Both scripts will:
1. Load the scientist biography documents
2. Create embeddings and vector stores
3. Answer sample questions about the scientists
4. Display the retrieval and generation results

The chunking script additionally compares different chunk sizes to show their impact.

## Common Issues

- **"No such file or directory"**: Make sure you're running from the project root, not inside the 01_basic_rag folder
- **OpenAI API errors**: Ensure your OPENAI_API_KEY environment variable is set
- **Import errors**: Run `uv sync` to install dependencies
- **libmagic warnings**: These are harmless but can be fixed with `brew install libmagic` on macOS

## Key Takeaways

1. **RAG is fundamentally simple**: Load documents, create embeddings, retrieve similar content, generate answers
2. **Chunking is crucial**: Proper text splitting dramatically improves retrieval quality
3. **Trade-offs matter**: Smaller chunks are more precise but may lack context; larger chunks have more context but less precision
4. **Experimentation is key**: Different datasets and use cases require different chunking strategies

## What's Next

Module 2 will introduce persistent vector stores (ChromaDB, FAISS) that save embeddings to disk and offer more advanced features than in-memory storage.