"""
InMemoryVectorStore Demo
========================

Demonstrates the simplest vector store option - storing embeddings in memory.
Perfect for development, testing, and small datasets where persistence isn't needed.
"""

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter

from dotenv import load_dotenv
load_dotenv(override=True)

# Load and chunk documents
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

# Create embeddings and in-memory vector store
embeddings = OpenAIEmbeddings()
in_memory_store = InMemoryVectorStore(embeddings)

# Add documents to store
in_memory_store.add_documents(documents=chunks)
print(f"✅ Added {len(chunks)} chunks to in-memory store")

# Create retriever
retriever = in_memory_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}
)

# Test similarity search directly
test_query = "What did Ada Lovelace contribute to computing?"
similar_docs = in_memory_store.similarity_search(test_query, k=3)

print(f"Query: {test_query}")
print(f"Found {len(similar_docs)} similar chunks:")
for i, doc in enumerate(similar_docs, 1):
    print(f"\nChunk {i}: {doc.page_content[:200]}...")

# Create RAG chain
print("\n🔗 Creating RAG chain...")
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

in_memory_rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Demo questions
questions = [
    "What programming concept did Ada Lovelace pioneer?",
    "How did Einstein's work change physics?",
    "What was Marie Curie's most important discovery?"
]

print("\n" + "="*50)
print("IN-MEMORY VECTOR STORE RAG DEMO")
print("="*50)

for i, question in enumerate(questions, 1):
    print(f"\nQ{i}: {question}")
    print("-" * 40)
    response = in_memory_rag_chain.invoke(question)
    print(f"A{i}: {response}")

# Demonstrate vector store properties
print("\n" + "="*50)
print("IN-MEMORY STORE PROPERTIES")
print("="*50)
print("✅ Advantages:")
print("  • Fast - no disk I/O overhead")
print("  • Simple - no external dependencies")
print("  • Perfect for development/testing")
print("  • No setup required")

print("\n❌ Limitations:")
print("  • Data lost when process ends")
print("  • Limited by available RAM")
print("  • No data sharing between processes")
print("  • Rebuild required on restart")

print(f"\n💡 Current store contains {len(chunks)} chunks in memory")
print("💡 Try: in_memory_rag_chain.invoke('Your question here')")
print("💡 Or: in_memory_store.similarity_search('Your query', k=5)")