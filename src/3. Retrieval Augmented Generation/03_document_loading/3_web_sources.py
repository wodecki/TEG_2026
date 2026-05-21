"""
Web Sources Loading
==================

Demonstrates loading content from web sources for RAG systems.
Shows web scraping, URL processing, and handling web-based content.
"""

from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
import requests
from bs4 import BeautifulSoup
import time

from dotenv import load_dotenv
load_dotenv(override=True)

def check_url_accessibility(url):
    """Check if a URL is accessible before processing."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    try:
        # Try HEAD first (faster)
        response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
        if response.status_code == 200:
            return True

        # If HEAD fails, try GET (some sites don't support HEAD)
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        return response.status_code == 200

    except requests.exceptions.RequestException as e:
        print(f"   🔍 Debug: {url} failed with {type(e).__name__}: {str(e)}")
        return False
    except Exception as e:
        print(f"   🔍 Debug: {url} failed with unexpected error: {str(e)}")
        return False

print("🌐 WEB SOURCES LOADING DEMONSTRATION")
print("="*50)

# 1. Define Wikipedia URLs for our scientists
print("\n1️⃣ Setting up web sources:")

# Wikipedia URLs for scientists (using simple English Wikipedia for cleaner content)
web_sources = {
    "Ada Lovelace": "https://simple.wikipedia.org/wiki/Ada_Lovelace",
    "Albert Einstein": "https://simple.wikipedia.org/wiki/Albert_Einstein",
    "Isaac Newton": "https://simple.wikipedia.org/wiki/Isaac_Newton",
    "Marie Curie": "https://simple.wikipedia.org/wiki/Marie_Curie"
}

print("   Configured web sources:")
for scientist, url in web_sources.items():
    print(f"   📖 {scientist}: {url}")

# 2. Test URL Accessibility
print("\n2️⃣ Testing URL accessibility:")
accessible_urls = {}
for scientist, url in web_sources.items():
    is_accessible = check_url_accessibility(url)
    status = "✅ Accessible" if is_accessible else "❌ Not accessible"
    print(f"   {scientist}: {status}")
    if is_accessible:
        accessible_urls[scientist] = url

print(f"   Found {len(accessible_urls)} accessible URLs")

# 3. Load Web Content
print("\n3️⃣ Loading web content:")

web_documents = []
if accessible_urls:
    for scientist, url in accessible_urls.items():
        print(f"   Loading: {scientist}")
        try:
            # Create WebBaseLoader with proper headers
            web_loader = WebBaseLoader(
                url,
                header_template={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
                }
            )

            # Load the content
            docs = web_loader.load()

            if docs:
                doc = docs[0]
                print(f"   📄 {scientist}: {len(doc.page_content)} characters")
                print(f"   🏷️ Metadata: {doc.metadata}")
                print(f"   📝 Preview: {doc.page_content[:150]}...")
                web_documents.extend(docs)
            else:
                print(f"   ⚠️ No content loaded for {scientist}")

            # Be respectful to servers
            time.sleep(1)

        except Exception as e:
            print(f"   ❌ Error loading {scientist}: {str(e)}")

else:
    print("   ❌ FATAL ERROR: No web sources are accessible.")
    raise RuntimeError("Cannot proceed: No accessible web sources found. Web loading demonstration requires internet access to Wikipedia.")

print(f"\n   Total web documents loaded: {len(web_documents)}")

# 4. Clean and Process Web Content
print("\n4️⃣ Processing web content:")

# Enhanced web content cleaning using BeautifulSoup
def clean_web_content_with_bs4(text, source_url):
    """Simple web content cleaning."""
    try:
        soup = BeautifulSoup(text, 'html.parser')

        # Remove unwanted elements
        for tag in ['nav', 'header', 'footer', 'script', 'style', 'noscript']:
            for element in soup.find_all(tag):
                element.decompose()

        # Get text content
        cleaned_text = soup.get_text(separator=' ', strip=True)

        # Basic cleanup
        import re
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        cleanup_phrases = ["Jump to navigation", "Jump to search", "[edit]"]
        for phrase in cleanup_phrases:
            cleaned_text = cleaned_text.replace(phrase, "")

        return cleaned_text.strip()

    except Exception as e:
        print(f"   ⚠️ Cleaning failed for {source_url}: {str(e)}")
        return ' '.join(text.split()).strip()

def extract_structured_content(html_content, source_url):
    """Extract basic structured content."""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract title
        title_elem = soup.find('title')
        title = title_elem.get_text(strip=True) if title_elem else ''

        # Extract headings
        headings = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3'])]

        # Extract main content
        main_content = clean_web_content_with_bs4(html_content, source_url)

        return {
            'title': title,
            'headings': headings[:5],  # First 5 headings
            'main_content': main_content
        }

    except Exception as e:
        print(f"   ⚠️ Extraction failed for {source_url}: {str(e)}")
        return None

# Clean web content
for doc in web_documents:
    original_length = len(doc.page_content)
    source_url = doc.metadata.get('source', '')
    scientist = source_url.split('/')[-1].replace('_', ' ')

    print(f"   🔍 Processing {scientist}...")

    # Extract content
    structured_content = extract_structured_content(doc.page_content, source_url)

    if structured_content:
        doc.page_content = structured_content['main_content']
        doc.metadata.update({
            'title': structured_content['title'],
            'headings': structured_content['headings'],
            'scientist': scientist,
            'content_type': 'web_structured'
        })

        cleaned_length = len(doc.page_content)
        print(f"   🧹 Cleaned: {original_length} → {cleaned_length} characters")

    else:
        doc.page_content = clean_web_content_with_bs4(doc.page_content, source_url)
        print(f"   🧹 Fallback cleaning applied")

# 5. Demonstrate BeautifulSoup Analysis
print("\n5️⃣ BeautifulSoup content analysis:")

if web_documents:
    sample_doc = web_documents[0]  # Analyze first document
    source_url = sample_doc.metadata.get('source', '')
    scientist = source_url.split('/')[-1].replace('_', ' ')

    print(f"   📊 Analysis of {scientist} page:")
    print(f"   🏷️  Title: {sample_doc.metadata.get('title', 'N/A')}")
    print(f"   📝 Introduction: {sample_doc.metadata.get('introduction', 'N/A')[:200]}...")

    headings = sample_doc.metadata.get('headings', [])
    if headings:
        print(f"   📋 Page structure ({len(headings)} sections):")
        for i, heading in enumerate(headings[:8], 1):  # Show first 8 headings
            print(f"      {i}. {heading}")
        if len(headings) > 8:
            print(f"      ... and {len(headings) - 8} more sections")

    print(f"   📄 Clean content length: {len(sample_doc.page_content)} characters")
    print(f"   🔍 Content preview: {sample_doc.page_content[:300]}...")

# 6. Text Splitting for Web Content
print("\n6️⃣ Chunking web content:")

web_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    # Web content often has different separators
    separators=["\n\n", "\n", ". ", " ", ""]
)

web_chunks = web_splitter.split_documents(web_documents)
print(f"   Created {len(web_chunks)} chunks from web content")

# Show chunk distribution
chunk_distribution = {}
for chunk in web_chunks:
    source = chunk.metadata.get('source', 'unknown')
    if 'wikipedia.org' in source or 'example.com' in source:
        scientist = source.split('/')[-1].replace('_', ' ')
        chunk_distribution[scientist] = chunk_distribution.get(scientist, 0) + 1

print("   Chunk distribution by scientist:")
for scientist, count in chunk_distribution.items():
    print(f"     {scientist}: {count} chunks")

# 7. Create Web-based RAG System
print("\n7️⃣ Creating web-based RAG system:")

embeddings = OpenAIEmbeddings()
web_vector_store = InMemoryVectorStore(embeddings)
web_vector_store.add_documents(documents=web_chunks)

web_retriever = web_vector_store.as_retriever(search_kwargs={"k": 4})
llm = ChatOpenAI(model="gpt-5.4-mini")

prompt = ChatPromptTemplate.from_template("""
You are an assistant for question-answering tasks.
Use the following pieces of retrieved context to answer the question.
The context comes from web sources and may contain some formatting artifacts.
If you don't know the answer, just say that you don't know.
Use three sentences maximum and keep the answer concise.

Question: {question}

Context: {context}

Answer:
""")

web_rag_chain = (
    {"context": web_retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 8. Test Web RAG System
print("\n8️⃣ Testing web-based RAG:")

web_questions = [
    "What are Ada Lovelace's most famous achievements?",
    "How did Einstein contribute to modern physics?",
    "What scientific discoveries is Marie Curie known for?"
]

for i, question in enumerate(web_questions, 1):
    print(f"\nQ{i}: {question}")
    print("-" * 40)
    try:
        response = web_rag_chain.invoke(question)
        print(f"A{i}: {response}")
    except Exception as e:
        print(f"A{i}: Error processing question: {str(e)}")


if web_documents:
    sample_doc = web_documents[0]
    headings_count = len(sample_doc.metadata.get('headings', []))
    print(f"\n  📈 Results for sample document:")
    print(f"    • Extracted {headings_count} section headings")
    print(f"    • Clean content: {len(sample_doc.page_content)} characters")
    print(f"    • Rich metadata: {len(sample_doc.metadata)} fields")

# 9. Web Loading Best Practices and Considerations
print("\n🌐 WEB LOADING BEST PRACTICES")
print("="*50)

print("✅ Web Loading Advantages:")
print("  • Access to up-to-date information")
print("  • Vast amount of available content")
print("  • Can supplement local documents")
print("  • Enables real-time knowledge updates")

print("\n⚠️ Web Loading Challenges:")
print("  • Content may change or disappear")
print("  • Requires internet connectivity")
print("  • Rate limiting and access restrictions")
print("  • Content quality varies widely")
print("  • Legal and ethical considerations")

print("\n🔧 Web Processing Best Practices:")
print("  • Respect robots.txt and rate limits")
print("  • Clean content of navigation elements")
print("  • Handle errors gracefully")
print("  • Cache content when appropriate")
print("  • Verify content quality and accuracy")

print("\n📊 When to Use Web Loading:")
print("  • Need current information")
print("  • Supplementing local knowledge base")
print("  • Research and fact-checking applications")
print("  • Building comprehensive knowledge systems")

print("\n⚖️ Legal and Ethical Considerations:")
print("  • Check website terms of service")
print("  • Respect copyright and fair use")
print("  • Don't overload servers with requests")
print("  • Consider data privacy implications")

print(f"\n💡 Web RAG chain ready: web_rag_chain.invoke('Your question')")
print(f"🌐 Processed {len(web_documents)} web documents, {len(web_chunks)} chunks")