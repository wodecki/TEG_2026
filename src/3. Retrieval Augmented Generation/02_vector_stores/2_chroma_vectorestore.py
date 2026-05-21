"""
ChromaDB Basic Usage
====================

Demonstrates persistent vector storage with ChromaDB.
Data is saved to disk and can be reloaded across sessions.
"""

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

from dotenv import load_dotenv
load_dotenv(override=True)

# Configuration
CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "scientists_bios"

def check_existing_collection():
    """Check if ChromaDB collection already exists."""
    if os.path.exists(CHROMA_DB_PATH):
        print(f"📁 Found existing ChromaDB at {CHROMA_DB_PATH}")
        return True
    return False

# Load and prepare documents
loader = DirectoryLoader(
    "data/scientists_bios",
    glob="*.txt",
    loader_cls=TextLoader,
    loader_kwargs={"encoding": "utf-8"},
)
docs = loader.load()
print(f"Loaded {len(docs)} documents")

# Split documents into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks = text_splitter.split_documents(docs)
print(f"Created {len(chunks)} chunks")

# Create embeddings
embeddings = OpenAIEmbeddings()

# Create or load ChromaDB collection
existing_db = check_existing_collection()

chroma_store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=CHROMA_DB_PATH
)

# Add documents if new collection or force refresh
if not existing_db:
    print("➕ Adding documents to new ChromaDB collection...")
    chroma_store.add_documents(documents=chunks)
    print(f"✅ Added {len(chunks)} chunks to ChromaDB")
else:
    # Check collection size
    collection_size = len(chroma_store.get()['ids'])
    print(f"📊 Existing collection has {collection_size} documents")

    if collection_size == 0:
        print("➕ Collection is empty, adding documents...")
        chroma_store.add_documents(documents=chunks)
        print(f"✅ Added {len(chunks)} chunks to ChromaDB")

# Create retriever
retriever = chroma_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 4}
)

# Test similarity search with scores
print("\n🔍 Testing similarity search with scores...")
test_query = "What did Marie Curie discover about radioactivity?"
similar_docs_with_scores = chroma_store.similarity_search_with_score(test_query, k=3)

print(f"Query: {test_query}")
print("Results with similarity scores:")
for i, (doc, score) in enumerate(similar_docs_with_scores, 1):
    print(f"\nChunk {i} (Score: {score:.3f}):")
    print(f"{doc.page_content[:150]}...")

# Create RAG chain
llm = ChatOpenAI(model="gpt-5.4-mini")

prompt = ChatPromptTemplate.from_template("""
You are an assistant for question-answering tasks.
Use the following pieces of retrieved context to answer the question.
If you don't know the answer, just say that you don't know.
Use three sentences maximum and keep the answer concise.

Question: {question}

Context: {context}

Answer:
""")

chroma_rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Demo questions
questions = [
    "What awards did Marie Curie receive?",
    "How did Charles Darwin develop his theory of evolution?",
    "What was Newton's contribution to mathematics?"
]


for i, question in enumerate(questions, 1):
    print(f"\nQ{i}: {question}")
    print("-" * 40)
    response = chroma_rag_chain.invoke(question)
    print(f"A{i}: {response}")

#================================================================================
# Load again to demonstrate persistence
print("\n🔄 Reloading ChromaDB to demonstrate persistence...")
chroma_store_reload = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=CHROMA_DB_PATH
)

# create a retriever for the reloaded store
retriever_reload = chroma_store_reload.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 4}
)

# create a RAG chain for the reloaded store
chroma_rag_chain_reload = (
    {"context": retriever_reload, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Perform a RAG query
response_reload = chroma_rag_chain_reload.invoke(questions[0])
print(f"\nAfter reload - Q1: {questions[0]}")
print(f"A1: {response_reload}")

#================================================================================
# Demonstrate ChromaDB features
# Get collection info
collection_info = chroma_store.get()
print(f"📊 Collection '{COLLECTION_NAME}' contains {len(collection_info['ids'])} documents")
print(f"💾 Persisted to: {CHROMA_DB_PATH}")

print("\n✅ ChromaDB Advantages:")
print("  • Persistent storage - survives restarts")
print("  • Efficient similarity search")
print("  • Built-in metadata support")
print("  • Incremental updates possible")
print("  • Great for production use")

print("\n🔄 Restart behavior:")
print("  • Next run will load existing data")
print("  • No need to re-embed documents")
print("  • Fast startup for existing collections")

print(f"\n💡 RAG chain ready: chroma_rag_chain.invoke('Your question')")
print(f"💡 Direct search: chroma_store.similarity_search('query', k=5)")
print(f"💡 With scores: chroma_store.similarity_search_with_score('query', k=3)")