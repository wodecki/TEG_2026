"""
FAISS Vector Store Introduction
===============================

Demonstrates FAISS (Facebook AI Similarity Search) for high-performance vector storage.
FAISS is optimized for speed and can handle large-scale similarity search efficiently.
"""

from langchain_community.document_loaders import DirectoryLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

from dotenv import load_dotenv
load_dotenv(override=True)

# Configuration
FAISS_INDEX_PATH = "./faiss_index"

def check_existing_index():
    """Check if FAISS index already exists."""
    if os.path.exists(f"{FAISS_INDEX_PATH}.faiss"):
        print(f"📁 Found existing FAISS index at {FAISS_INDEX_PATH}")
        return True
    return False

# Load and prepare documents
print("📚 Loading documents...")
loader = DirectoryLoader("data/scientists_bios")
docs = loader.load()
print(f"Loaded {len(docs)} documents")

# Split documents into chunks
print("✂️ Chunking documents...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks = text_splitter.split_documents(docs)
print(f"Created {len(chunks)} chunks")

# Create embeddings
embeddings = OpenAIEmbeddings()

# Create or load FAISS index
print("⚡ Setting up FAISS vector store...")
existing_index = check_existing_index()

if existing_index:
    print("📖 Loading existing FAISS index...")
    faiss_store = FAISS.load_local(
        FAISS_INDEX_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )
    print(f"✅ Loaded existing FAISS index with {faiss_store.index.ntotal} vectors")
else:
    print("🔨 Creating new FAISS index from documents...")
    faiss_store = FAISS.from_documents(chunks, embeddings)

    # Save the index to disk
    print("💾 Saving FAISS index to disk...")
    faiss_store.save_local(FAISS_INDEX_PATH)
    print(f"✅ Created and saved FAISS index with {faiss_store.index.ntotal} vectors")

# Create retriever
retriever = faiss_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 4}
)

# Test similarity search with FAISS
print("\n🔍 Testing FAISS similarity search...")
test_query = "What theories did Einstein develop?"
similar_docs = faiss_store.similarity_search(test_query, k=3)

print(f"Query: {test_query}")
print(f"Found {len(similar_docs)} similar chunks:")
for i, doc in enumerate(similar_docs, 1):
    print(f"\nChunk {i}: {doc.page_content[:200]}...")

# Test similarity search with scores
print("\n📊 Testing similarity search with scores...")
similar_docs_with_scores = faiss_store.similarity_search_with_score(test_query, k=3)
print("Results with FAISS distance scores (lower = more similar):")
for i, (doc, score) in enumerate(similar_docs_with_scores, 1):
    print(f"\nChunk {i} (Distance: {score:.3f}):")
    print(f"{doc.page_content[:150]}...")

# Create RAG chain
print("\n🔗 Creating RAG chain with FAISS...")
llm = ChatOpenAI(model="gpt-4o-mini")

prompt = ChatPromptTemplate.from_template("""
You are an assistant for question-answering tasks.
Use the following pieces of retrieved context to answer the question.
If you don't know the answer, just say that you don't know.
Use three sentences maximum and keep the answer concise.

Question: {question}

Context: {context}

Answer:
""")

faiss_rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Demo questions
questions = [
    "What was Einstein's theory of relativity about?",
    "How did Darwin's voyage influence his thinking?",
    "What programming concepts did Ada Lovelace pioneer?"
]

print("\n" + "="*50)
print("FAISS HIGH-PERFORMANCE RAG DEMO")
print("="*50)

for i, question in enumerate(questions, 1):
    print(f"\nQ{i}: {question}")
    print("-" * 40)
    response = faiss_rag_chain.invoke(question)
    print(f"A{i}: {response}")

# Demonstrate FAISS capabilities
print("\n" + "="*50)
print("FAISS FEATURES & PERFORMANCE")
print("="*50)

print(f"📊 Index contains {faiss_store.index.ntotal} vectors")
print(f"🔢 Vector dimension: {faiss_store.index.d}")
print(f"💾 Index saved to: {FAISS_INDEX_PATH}.faiss")

print("\n⚡ FAISS Advantages:")
print("  • Extremely fast similarity search")
print("  • Memory efficient for large datasets")
print("  • GPU acceleration available (faiss-gpu)")
print("  • Multiple index types (Flat, IVF, HNSW)")
print("  • Optimized for production workloads")

print("\n🏗️ FAISS vs Other Stores:")
print("  • Faster than ChromaDB for large scales")
print("  • More memory efficient than InMemory")
print("  • Less features than full databases")
print("  • Perfect for read-heavy workloads")

print("\n🔄 Persistence:")
print("  • Index automatically saved/loaded")
print("  • Fast startup with existing index")
print("  • Single file storage (.faiss + .pkl)")

print(f"\n💡 RAG chain ready: faiss_rag_chain.invoke('Your question')")
print(f"💡 Fast search: faiss_store.similarity_search('query', k=5)")
print(f"💡 With scores: faiss_store.similarity_search_with_score('query', k=3)")