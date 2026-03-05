"""
RAG with Text Chunking
======================

Enhanced RAG system that splits documents into smaller chunks for better retrieval.
This improves retrieval accuracy by creating more focused, searchable text segments.
"""

from langchain_community.document_loaders import DirectoryLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load environment variables from .env file, override if already set
from dotenv import load_dotenv
load_dotenv(override=True) 

# Load documents
loader = DirectoryLoader("data/scientists_bios")
docs = loader.load()
print(f"Loaded {len(docs)} documents")

# Chunk documents
chunk_size=1000 
chunk_overlap=200

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap,
    separators=["\n\n", "\n", ". ", " ", ""]
)

chunks = text_splitter.split_documents(docs)
print(f"Created {len(chunks)} text chunks")

# Create embeddings and vector store
embeddings = OpenAIEmbeddings()
vector_store = InMemoryVectorStore(embeddings)
vector_store.add_documents(documents=chunks)

retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 4}
)

# Initialize LLM and prompt
llm = ChatOpenAI(model="gpt-5-nano")

prompt = ChatPromptTemplate.from_template("""
You are an assistant for question-answering tasks.
Use the following pieces of retrieved context to answer the question.
The context consists of multiple text chunks that may contain relevant information.
If you don't know the answer, just say that you don't know.
Use three sentences maximum and keep the answer concise.

Question: {question}

Context: {context}

Answer:
""")

# Create RAG chain
chunked_rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)


# Sample questions for testing
questions = [
    "What collaboration did Ada Lovelace have with Charles Babbage?",
    "How did Newton's work during the Great Plague contribute to his discoveries?",
    "What awards did Marie Curie receive during her lifetime?"
]


for i, question in enumerate(questions, 1):
    print(f"\nQ{i}: {question}")
    print("-" * 50)
    response = chunked_rag_chain.invoke(question)
    print(f"A{i}: {response}")

# Compare different chunk sizes

def create_chunked_rag(chunk_size, overlap): # A helper function to create RAG chain with specified chunk size and overlap
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = text_splitter.split_documents(docs)
    
    vector_store = InMemoryVectorStore(embeddings)
    vector_store.add_documents(documents=chunks)
    
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )
    
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain, len(chunks)

# Different chunk size and overlap configurations to test
chunk_configs = [
    (500, 50),   # Small chunks
    (1000, 200), # Medium chunks
    (2000, 400)  # Large chunks
]

test_question = "What was Ada Lovelace's contribution to computer programming?"
print("Question: " + test_question + "\n")

for chunk_size, overlap in chunk_configs:
    print(f"\n📊 Chunk Size: {chunk_size}, Overlap: {overlap}")
    print("-" * 40)

    rag_chain, num_chunks = create_chunked_rag(chunk_size, overlap)
    response = rag_chain.invoke(test_question)

    print(f"Total chunks: {num_chunks}")
    print(f"Answer: {response}")