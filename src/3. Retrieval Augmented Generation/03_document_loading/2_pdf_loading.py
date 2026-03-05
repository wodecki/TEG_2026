"""
PDF Document Loading
===================

Demonstrates loading and processing PDF documents for RAG systems.
Shows PDF creation, loading, and comparison with text-based approaches.
"""

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter

# PDF generation libraries
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
import os

from dotenv import load_dotenv
load_dotenv(override=True)

def create_pdf_from_text(text_file_path, pdf_file_path):
    """Convert a text file to PDF for demonstration purposes."""

    # Read the text file
    with open(text_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Create a PDF document
    doc = SimpleDocTemplate(pdf_file_path, pagesize=letter)
    styles = getSampleStyleSheet()

    # Create custom styles
    title_style = ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=TA_LEFT,
        spaceAfter=20
    )

    normal_style = ParagraphStyle(
        name='CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_LEFT,
        spaceAfter=12
    )

    # Split content into title and body
    lines = content.split('\n')
    title = lines[0] if lines else "Document"
    body_content = '\n'.join(lines[1:]) if len(lines) > 1 else content

    # Create story (document content)
    story = []

    # Add title
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 20))

    # Add body content (split into paragraphs)
    paragraphs = body_content.split('\n\n')
    for para in paragraphs:
        if para.strip():
            # Clean up the paragraph text for PDF
            clean_para = para.strip().replace('\n', ' ')
            story.append(Paragraph(clean_para, normal_style))
            story.append(Spacer(1, 12))

    # Build PDF
    doc.build(story)
    print(f"   ✅ Created PDF: {pdf_file_path}")

print("📄 PDF DOCUMENT LOADING DEMONSTRATION")
print("="*50)

# 1. Create PDF versions of text files for demonstration
print("\n1️⃣ Creating PDF files from text sources:")

# Create PDFs directory if it doesn't exist
pdf_dir = "data/pdfs"
os.makedirs(pdf_dir, exist_ok=True)

# Convert some text files to PDF
text_files = [
    "data/scientists_bios/Ada Lovelace.txt",
    "data/scientists_bios/Albert Einstein.txt"
]

pdf_files = []
for text_file in text_files:
    scientist_name = os.path.basename(text_file).replace('.txt', '')
    pdf_file = os.path.join(pdf_dir, f"{scientist_name}.pdf")

    if not os.path.exists(pdf_file):
        create_pdf_from_text(text_file, pdf_file)
    else:
        print(f"   📄 PDF already exists: {pdf_file}")

    pdf_files.append(pdf_file)

# 2. Load PDF Documents
print("\n2️⃣ Loading PDF documents:")

pdf_documents = []
for pdf_file in pdf_files:
    print(f"   Loading: {pdf_file}")

    # Load PDF using PyPDFLoader
    pdf_loader = PyPDFLoader(pdf_file)
    pdf_docs = pdf_loader.load()

    scientist_name = os.path.basename(pdf_file).replace('.pdf', '')
    print(f"   📄 {scientist_name}: {len(pdf_docs)} pages")

    # Show page information
    for i, page in enumerate(pdf_docs):
        print(f"      Page {i+1}: {len(page.page_content)} characters")
        print(f"      Metadata: {page.metadata}")

    pdf_documents.extend(pdf_docs)

print(f"\n   Total PDF documents loaded: {len(pdf_documents)}")

# 3. Compare PDF vs Text Loading
print("\n3️⃣ Comparing PDF vs Text loading:")

# Load the same content as text
text_loader = TextLoader("data/scientists_bios/Ada Lovelace.txt")
text_doc = text_loader.load()[0]

# Find corresponding PDF
ada_pdf_docs = [doc for doc in pdf_documents if "Ada Lovelace" in doc.metadata.get('source', '')]

print("   Ada Lovelace comparison:")
print(f"   📄 Text version: {len(text_doc.page_content)} characters")
print(f"   📄 PDF version: {sum(len(doc.page_content) for doc in ada_pdf_docs)} characters")
print(f"   📄 PDF pages: {len(ada_pdf_docs)}")

# Show content preview
print(f"\n   Text preview: {text_doc.page_content[:200]}...")
print(f"   PDF preview: {ada_pdf_docs[0].page_content[:200]}...")

# 4. Text Splitting with PDFs
print("\n4️⃣ Text splitting PDF documents:")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

# Split PDF documents
pdf_chunks = text_splitter.split_documents(pdf_documents)
print(f"   PDF chunks created: {len(pdf_chunks)}")

# Show chunk distribution by source
chunk_by_source = {}
for chunk in pdf_chunks:
    source = chunk.metadata.get('source', 'unknown')
    scientist = os.path.basename(source).replace('.pdf', '')
    chunk_by_source[scientist] = chunk_by_source.get(scientist, 0) + 1

print("   Chunks per scientist (PDF):")
for scientist, count in chunk_by_source.items():
    print(f"     {scientist}: {count} chunks")

# 5. Create RAG System with PDF Documents
print("\n5️⃣ Creating RAG system with PDF documents:")

embeddings = OpenAIEmbeddings()
pdf_vector_store = InMemoryVectorStore(embeddings)
pdf_vector_store.add_documents(documents=pdf_chunks)

pdf_retriever = pdf_vector_store.as_retriever(search_kwargs={"k": 3})
llm = ChatOpenAI(model="gpt-5-nano")

prompt = ChatPromptTemplate.from_template("""
You are an assistant for question-answering tasks.
Use the following pieces of retrieved context to answer the question.
The context comes from PDF documents that may have formatting artifacts.
If you don't know the answer, just say that you don't know.
Use three sentences maximum and keep the answer concise.

Question: {question}

Context: {context}

Answer:
""")

pdf_rag_chain = (
    {"context": pdf_retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 6. Test PDF RAG System
print("\n6️⃣ Testing PDF-based RAG:")

test_questions = [
    "What was Ada Lovelace's contribution to programming?",
    "How did Einstein develop his theories of relativity?"
]

for i, question in enumerate(test_questions, 1):
    print(f"\nQ{i}: {question}")
    print("-" * 40)
    response = pdf_rag_chain.invoke(question)
    print(f"A{i}: {response}")

# 7. PDF Loading Best Practices
print("\n📋 PDF LOADING BEST PRACTICES")
print("="*50)

print("✅ Advantages of PDF Loading:")
print("  • Preserves document structure and formatting")
print("  • Handles multi-page documents naturally")
print("  • Maintains page-level metadata")
print("  • Good for official documents, reports, papers")

print("\n⚠️ PDF Loading Considerations:")
print("  • May include formatting artifacts")
print("  • OCR quality affects text extraction")
print("  • Complex layouts can cause text jumbling")
print("  • Larger file sizes than plain text")

print("\n🔧 PDF Processing Tips:")
print("  • Use page-aware chunking strategies")
print("  • Clean extracted text of artifacts")
print("  • Consider PDF structure in retrieval")
print("  • Test with your specific PDF types")

print("\n📊 When to Use PDF Loading:")
print("  • Official documents and reports")
print("  • Academic papers and publications")
print("  • Multi-page structured content")
print("  • When document layout matters")

print(f"\n💡 PDF RAG chain ready: pdf_rag_chain.invoke('Your question')")
print(f"📄 Processed {len(pdf_documents)} PDF pages, {len(pdf_chunks)} chunks")