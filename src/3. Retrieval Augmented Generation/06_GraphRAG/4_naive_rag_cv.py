#!/usr/bin/env python3
"""
Naive RAG Baseline for CV Data
==============================

Traditional vector-based RAG system using ChromaDB for similarity search.
This serves as the baseline comparison against GraphRAG to demonstrate
the limitations of naive RAG for structured queries.
"""

from dotenv import load_dotenv
load_dotenv(override=True)

import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
import toml

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NaiveRAGSystem:
    """Traditional RAG system using vector similarity search."""

    def __init__(self, config_path: str = "utils/config.toml"):
        """Initialize the Naive RAG system."""
        self.config = self._load_config(config_path)

        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=os.getenv("OPENAI_API_KEY")
        )

        self.llm = ChatOpenAI(
            model="gpt-4o",  # Same model as GraphRAG for fair comparison
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

        # Directories
        self.data_dir = Path(self.config['output']['programmers_dir'])
        self.vector_db_dir = Path("./chroma_naive_rag_cv")
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)

        # Will be initialized when needed
        self.vectorstore = None
        self.retriever = None
        self.rag_chain = None

        logger.info("✓ Naive RAG System initialized")

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from TOML file."""
        if not os.path.exists(config_path):
            raise ValueError(f"Configuration file not found: {config_path}")

        with open(config_path, 'r') as f:
            config = toml.load(f)

        return config

    def load_cv_documents(self) -> List[Dict[str, Any]]:
        """Load and process all CV PDF documents."""
        cv_files = list(self.data_dir.glob("*.pdf"))

        if not cv_files:
            raise FileNotFoundError(f"No PDF files found in {self.data_dir}")

        logger.info(f"Loading {len(cv_files)} CV files...")

        documents = []
        for cv_file in sorted(cv_files):
            try:
                loader = PyPDFLoader(str(cv_file))
                docs = loader.load()

                # Add metadata
                for doc in docs:
                    doc.metadata.update({
                        "source_file": cv_file.name,
                        "document_type": "cv",
                        "person_name": cv_file.stem
                    })

                documents.extend(docs)

            except Exception as e:
                logger.warning(f"Could not load {cv_file}: {e}")
                continue

        logger.info(f"✓ Loaded {len(documents)} document pages from {len(cv_files)} CVs")
        return documents

    def create_vector_store(self, force_recreate: bool = False) -> None:
        """Create or load the vector store."""
        if self.vector_db_dir.exists() and not force_recreate:
            logger.info("Loading existing vector store...")
            self.vectorstore = Chroma(
                persist_directory=str(self.vector_db_dir),
                embedding_function=self.embeddings
            )
            logger.info("✓ Vector store loaded")
        else:
            logger.info("Creating new vector store...")

            # Load documents
            documents = self.load_cv_documents()

            # Split documents into chunks
            logger.info("Splitting documents into chunks...")
            texts = self.text_splitter.split_documents(documents)
            logger.info(f"✓ Created {len(texts)} text chunks")

            # Create vector store
            logger.info("Creating embeddings and vector store...")
            self.vectorstore = Chroma.from_documents(
                documents=texts,
                embedding=self.embeddings,
                persist_directory=str(self.vector_db_dir)
            )
            logger.info("✓ Vector store created and saved")

    def setup_rag_chain(self) -> None:
        """Setup the RAG chain for question answering."""
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized. Call create_vector_store() first.")

        # Create retriever
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}  # Retrieve top 5 similar chunks
        )

        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an HR assistant helping with CV analysis. Use the provided context from CVs to answer questions accurately.

IMPORTANT INSTRUCTIONS:
- Base your answers ONLY on the information provided in the context
- For counting questions, provide your best estimate based on the visible context
- For listing questions, list what you can see in the context
- For questions requiring aggregation, provide approximations if exact calculations aren't possible
- If you cannot determine something from the context, say so clearly
- Be specific about names, skills, and details when they appear in the context
- If the context is incomplete for a full answer, acknowledge this limitation

Context from CVs:
{context}"""),
            ("human", "{question}")
        ])

        # Create the RAG chain
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        self.rag_chain = (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

        logger.info("✓ RAG chain configured")

    def query(self, question: str) -> Dict[str, Any]:
        """Process a query through the Naive RAG system."""
        start_time = time.time()

        try:
            if self.rag_chain is None:
                raise ValueError("RAG chain not initialized. Call setup_rag_chain() first.")

            logger.info(f"Processing query: {question}")

            # Get relevant documents for debugging
            relevant_docs = self.retriever.invoke(question)

            # Generate answer
            answer = self.rag_chain.invoke(question)

            execution_time = time.time() - start_time

            # Format context for storage
            context_info = []
            for i, doc in enumerate(relevant_docs):
                context_info.append({
                    "chunk_index": i,
                    "source_file": doc.metadata.get("source_file", "unknown"),
                    "person_name": doc.metadata.get("person_name", "unknown"),
                    "content_preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                })

            result = {
                "query": question,
                "answer": answer,
                "source_type": "naive_rag",
                "execution_time": execution_time,
                "num_chunks_retrieved": len(relevant_docs),
                "context_info": context_info,
                "success": True
            }

            logger.info(f"✓ Query processed in {execution_time:.2f}s")
            return result

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            execution_time = time.time() - start_time

            return {
                "query": question,
                "answer": f"Error processing query: {str(e)}",
                "source_type": "naive_rag",
                "execution_time": execution_time,
                "num_chunks_retrieved": 0,
                "context_info": [],
                "success": False,
                "error": str(e)
            }

    def initialize_system(self, force_recreate_vectorstore: bool = False) -> bool:
        """Initialize the complete RAG system."""
        try:
            # Create/load vector store
            self.create_vector_store(force_recreate=force_recreate_vectorstore)

            # Setup RAG chain
            self.setup_rag_chain()

            logger.info("✓ Naive RAG system fully initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize system: {e}")
            return False

    def validate_system(self) -> bool:
        """Validate that the system is working correctly."""
        try:
            # Test query
            test_result = self.query("How many people are in the database?")

            if test_result["success"]:
                logger.info("✓ System validation successful")
                print(f"Test query result: {test_result['answer'][:100]}...")
                return True
            else:
                logger.error("System validation failed")
                return False

        except Exception as e:
            logger.error(f"System validation error: {e}")
            return False

    def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database."""
        if self.vectorstore is None:
            return {"error": "Vector store not initialized"}

        try:
            # Get collection info
            collection = self.vectorstore._collection
            total_chunks = collection.count()

            # Get sample of source files
            sample_results = self.vectorstore.similarity_search("", k=10)
            source_files = set()
            for doc in sample_results:
                source_files.add(doc.metadata.get("source_file", "unknown"))

            stats = {
                "total_chunks": total_chunks,
                "sample_source_files": list(source_files)[:10],
                "embedding_model": "text-embedding-3-small",
                "chunk_size": 1000,
                "chunk_overlap": 200
            }

            return stats

        except Exception as e:
            return {"error": f"Could not get stats: {e}"}


def test_naive_rag_system():
    """Test the Naive RAG system with sample queries."""
    print("Testing Naive RAG System")
    print("=" * 30)

    # Initialize system
    rag_system = NaiveRAGSystem()

    if not rag_system.initialize_system():
        print("❌ Failed to initialize system")
        return

    # Show database stats
    stats = rag_system.get_database_stats()
    print(f"\nDatabase Statistics:")
    print(f"Total chunks: {stats.get('total_chunks', 'unknown')}")
    print(f"Sample files: {', '.join(stats.get('sample_source_files', [])[:3])}")

    # Validate system
    if not rag_system.validate_system():
        print("❌ System validation failed")
        return

    # Test queries representing different types
    test_queries = [
        "How many people have Python skills?",
        "List people with AWS certifications",
        "What is the most common programming language?",
        "Who worked at Google?",
        "Find people with both React and Node.js skills"
    ]

    print(f"\nTesting with {len(test_queries)} sample queries...")
    results = []

    for i, query in enumerate(test_queries):
        print(f"\n[{i+1}/{len(test_queries)}] Query: {query}")
        print("-" * 40)

        result = rag_system.query(query)
        results.append(result)

        if result["success"]:
            print(f"Answer: {result['answer']}")
            print(f"Execution time: {result['execution_time']:.2f}s")
            print(f"Chunks used: {result['num_chunks_retrieved']}")
        else:
            print(f"❌ Error: {result['answer']}")

    # Save test results
    output_file = Path("results") / "naive_rag_test_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            "test_metadata": {
                "system_type": "naive_rag",
                "test_queries": len(test_queries),
                "database_stats": stats
            },
            "results": results
        }, f, indent=2)

    print(f"\n✓ Test results saved to: {output_file}")
    print("\nNext step: Run uv run python utils/generate_ground_truth.py")


def main():
    """Main function for naive RAG baseline."""
    print("Naive RAG Baseline System for CV Data")
    print("=" * 40)

    # Ensure results directory exists
    os.makedirs("results", exist_ok=True)

    # Test the system
    test_naive_rag_system()


if __name__ == "__main__":
    main()