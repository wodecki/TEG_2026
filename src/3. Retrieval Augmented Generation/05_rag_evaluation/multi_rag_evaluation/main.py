from dotenv import load_dotenv
load_dotenv(override=True)

import os
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI

from rag_systems import (
    NaiveRAG,
    MetadataFilteringRAG,
    HybridSearchRAG,
    QueryExpansionRAG,
    RerankingRAG
)
from evaluation import RAGEvaluator
from config import settings

def load_and_chunk(data_dir):
    """Load and chunk documents for all RAG systems."""
    loader = DirectoryLoader(data_dir, glob="*.txt")
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP
    )
    return splitter.split_documents(docs)

def main():
    print("="*80)
    print("MULTI-RAG SYSTEM COMPARATIVE EVALUATION")
    print("="*80)

    # Validate environment
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY not found in environment")

    data_dir = "data/scientists_bios"
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    # 1. Load and prepare data
    print(f"\n📚 Loading documents from {data_dir}...")
    chunks = load_and_chunk(data_dir)
    print(f"✓ Created {len(chunks)} chunks")

    # 2. Initialize RAG systems
    print(f"\n🔧 Initializing RAG systems...")
    config = settings.get_config()

    rag_systems = [
        NaiveRAG(chunks, config),
        MetadataFilteringRAG(chunks, config),
        HybridSearchRAG(chunks, config),
        QueryExpansionRAG(chunks, config),
        RerankingRAG(chunks, config)
    ]

    # 3. Build all systems
    print(f"\n🏗️ Building RAG systems...")
    successful_systems = []

    for rag in rag_systems:
        try:
            print(f"   Building {rag.name}...")
            rag.build()
            successful_systems.append(rag)
            print(f"   ✓ {rag.name} built successfully")
        except Exception as e:
            print(f"   ✗ Failed to build {rag.name}: {e}")

    if not successful_systems:
        print("❌ No RAG systems built successfully")
        return

    print(f"✓ Successfully built {len(successful_systems)} RAG systems")

    # 4. Initialize evaluator
    print(f"\n📊 Setting up evaluation...")
    try:
        expert_llm = ChatOpenAI(model=settings.EXPERT_MODEL)
        evaluator_llm = ChatOpenAI(model=settings.EVALUATOR_MODEL)

        evaluator = RAGEvaluator(
            expert_llm=expert_llm,
            evaluator_llm=evaluator_llm
        )
        print("✓ Evaluator initialized")
    except Exception as e:
        print(f"❌ Failed to initialize evaluator: {e}")
        return

    # 5. Run comparative evaluation
    print(f"\n🏃 Running evaluations...")
    print(f"Questions to evaluate: {len(settings.EVAL_QUESTIONS)}")

    try:
        results = evaluator.compare_systems(
            rag_systems=successful_systems,
            questions=settings.EVAL_QUESTIONS,
            data_dir=data_dir
        )

        if not results:
            print("❌ No evaluation results obtained")
            return

        print(f"✓ Evaluated {len(results)} systems")

    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        return

    # 6. Display and save results
    print(f"\n📈 Processing results...")
    try:
        comparison_df = evaluator.create_comparison_dataframe(results)
        evaluator.print_comparison_table(comparison_df)

        # Save results
        results_dir = "results"
        evaluator.save_results(comparison_df, results_dir)

        print(f"\n🎉 Evaluation completed successfully!")
        print(f"📁 Detailed results saved in '{results_dir}/' directory")

    except Exception as e:
        print(f"❌ Failed to process results: {e}")

if __name__ == "__main__":
    main()