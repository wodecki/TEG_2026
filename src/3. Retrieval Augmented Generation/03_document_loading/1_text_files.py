"""
Text File Loading Basics
========================

Demonstrates different approaches to loading text files for RAG systems.
Shows single file, multiple files, and directory-based loading patterns.
"""

from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter

from dotenv import load_dotenv
load_dotenv(override=True)

print("📄 TEXT FILE LOADING DEMONSTRATION")
print("="*50)

# 1. Single File Loading
print("\n1️⃣ Loading a single text file:")
single_file_loader = TextLoader("data/scientists_bios/Ada Lovelace.txt")
single_doc = single_file_loader.load()

print(f"   Loaded: {len(single_doc)} document")
print(f"   Content length: {len(single_doc[0].page_content)} characters")
print(f"   Metadata: {single_doc[0].metadata}")
print(f"   Preview: {single_doc[0].page_content[:200]}...")

# 2. Multiple Specific Files
print("\n2️⃣ Loading multiple specific files:")
files_to_load = [
    "data/scientists_bios/Ada Lovelace.txt",
    "data/scientists_bios/Albert Einstein.txt",
    "data/scientists_bios/Isaac Newton.txt"
]

multiple_docs = []
for file_path in files_to_load:
    loader = TextLoader(file_path)
    docs = loader.load()
    multiple_docs.extend(docs)

print(f"   Loaded: {len(multiple_docs)} documents")
for i, doc in enumerate(multiple_docs):
    scientist_name = doc.metadata['source'].split('/')[-1].replace('.txt', '')
    print(f"   File {i+1}: {scientist_name} ({len(doc.page_content)} chars)")

# 3. Directory Loading (All Files)
print("\n3️⃣ Loading entire directory:")
directory_loader = DirectoryLoader("data/scientists_bios")
all_docs = directory_loader.load()

print(f"   Loaded: {len(all_docs)} documents from directory")
for i, doc in enumerate(all_docs):
    scientist_name = doc.metadata['source'].split('/')[-1].replace('.txt', '')
    print(f"   Document {i+1}: {scientist_name} ({len(doc.page_content)} chars)")

# 4. Directory Loading with File Pattern
print("\n4️⃣ Loading with glob pattern (*.txt files only):")
pattern_loader = DirectoryLoader(
    "data/scientists_bios",
    glob="*.txt"
)
pattern_docs = pattern_loader.load()

print(f"   Loaded: {len(pattern_docs)} .txt documents")

# 5. Demonstrate Text Splitting on Loaded Documents
print("\n5️⃣ Text splitting demonstration:")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

# Split all documents
all_chunks = text_splitter.split_documents(all_docs)
print(f"   Original documents: {len(all_docs)}")
print(f"   After chunking: {len(all_chunks)} chunks")

# Show chunk distribution per scientist
chunk_distribution = {}
for chunk in all_chunks:
    scientist_name = chunk.metadata['source'].split('/')[-1].replace('.txt', '')
    chunk_distribution[scientist_name] = chunk_distribution.get(scientist_name, 0) + 1

print("   Chunk distribution:")
for scientist, count in chunk_distribution.items():
    print(f"     {scientist}: {count} chunks")

# 6. Create RAG System with Different Loading Approaches
print("\n6️⃣ Creating RAG system:")
embeddings = OpenAIEmbeddings()
vector_store = InMemoryVectorStore(embeddings)
vector_store.add_documents(documents=all_chunks)

retriever = vector_store.as_retriever(search_kwargs={"k": 3})
llm = ChatOpenAI(model="gpt-5-nano")

prompt = ChatPromptTemplate.from_template("""
You are an assistant for question-answering tasks.
Use the following pieces of retrieved context to answer the question.
If you don't know the answer, just say that you don't know.
Use three sentences maximum and keep the answer concise.

Question: {question}

Context: {context}

Answer:
""")

text_rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Test with questions about different scientists
test_questions = [
    "What did Ada Lovelace contribute to computing?",
    "How did Einstein develop his theories?",
    "What was Newton's most famous work?"
]

print("\n🔍 Testing RAG with loaded text files:")
for i, question in enumerate(test_questions, 1):
    print(f"\nQ{i}: {question}")
    print("-" * 40)
    response = text_rag_chain.invoke(question)
    print(f"A{i}: {response}")

# 7. Comparison of Loading Methods
print("\n📊 LOADING METHOD COMPARISON")
print("="*50)
print("Method 1 - Single File:")
print("  ✅ Precise control over content")
print("  ✅ Fast for specific documents")
print("  ❌ Manual file specification")
print("  ❌ Doesn't scale well")

print("\nMethod 2 - Multiple Specific Files:")
print("  ✅ Selective loading")
print("  ✅ Good for curated data")
print("  ❌ Requires file list maintenance")
print("  ❌ Manual process")

print("\nMethod 3 - Directory Loading:")
print("  ✅ Automatic discovery")
print("  ✅ Scales with directory content")
print("  ✅ No file list maintenance")
print("  ❌ Loads everything (might include unwanted files)")

print("\nMethod 4 - Pattern-Based Loading:")
print("  ✅ Flexible filtering")
print("  ✅ Automatic but selective")
print("  ✅ Good for mixed directories")
print("  ✅ Best of both worlds")

print(f"\n💡 Text RAG chain ready: text_rag_chain.invoke('Your question')")
print(f"📚 Loaded {len(all_docs)} documents, {len(all_chunks)} chunks total")