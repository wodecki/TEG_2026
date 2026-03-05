"""
Minimal RAG Implementation
==========================

A simple RAG (Retrieval Augmented Generation) system using in-memory vector store.
This script demonstrates the core RAG concepts without external vector databases.
"""

from langchain_community.document_loaders import DirectoryLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from dotenv import load_dotenv
load_dotenv(override=True) # Load environment variables from .env file, override if already set


# 1. Load documents
print("Loading documents...")
loader = DirectoryLoader("data/scientists_bios")
docs = loader.load()
print(f"Loaded {len(docs)} documents")

# 2. Create embeddings and vector store
embeddings = OpenAIEmbeddings()
vector_store = InMemoryVectorStore(embeddings)
vector_store.add_documents(documents=docs)

# 3. Create retriever
retriever = vector_store.as_retriever()

# 4. Create LLM
llm = ChatOpenAI(model="gpt-5-nano")

# 5. Create prompt template
prompt = ChatPromptTemplate.from_template("""
You are an assistant for question-answering tasks.
Use the following pieces of retrieved context to answer the question.
If you don't know the answer, just say that you don't know.
Use three sentences maximum and keep the answer concise.

Question: {question}

Context: {context}

Answer:
""")

# 6. Create RAG chain
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Answer a single question using the RAG system
question = "What was Ada Lovelace's contribution to computer programming?"
response = rag_chain.invoke(question)
print(f"Q: {question}")
print(f"A: {response}")


# Sample questions for testing
questions = [
    "What was Ada Lovelace's contribution to computer programming?",
    "How did Einstein develop his theory of relativity?",
    "What was Newton's most important discovery?"
]

# Answer multiple questions using the RAG system

for i, question in enumerate(questions, 1):
    print(f"\nQ{i}: {question}")
    print("-" * 40)
    response = rag_chain.invoke(question)
    print(f"A{i}: {response}")
