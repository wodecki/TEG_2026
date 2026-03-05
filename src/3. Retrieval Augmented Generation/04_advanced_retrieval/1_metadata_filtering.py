"""
Metadata Filtering for Advanced Retrieval
=========================================

Demonstrates how metadata filtering enhances retrieval precision and relevance.
Shows contextual retrieval strategies using document properties and attributes.
"""

from langchain_community.document_loaders import DirectoryLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

from dotenv import load_dotenv
load_dotenv(override=True)

print("🎯 METADATA FILTERING DEMONSTRATION")
print("="*50)

# 1. Load Documents with Enhanced Metadata
print("\n1️⃣ Loading documents with rich metadata:")

# Load existing scientist documents
data_dir = "data/scientists_bios"
loader = DirectoryLoader(data_dir, glob="*.txt")
raw_documents = loader.load()

print(f"   Loaded {len(raw_documents)} raw documents")

# Enhanced metadata extraction
def extract_enhanced_metadata(doc):
    """Extract rich metadata from document content and filename."""
    source_file = doc.metadata.get('source', '')
    filename = os.path.basename(source_file).replace('.txt', '')
    content = doc.page_content

    # Extract scientist information
    scientist_info = {
        'scientist_name': filename,
        'content_type': 'biography',
        'source_type': 'text_file',
        'language': 'english'
    }

    # Extract time periods from content
    birth_death_info = {}
    if '(' in content and ')' in content:
        # Look for birth-death years in parentheses
        import re
        years = re.findall(r'\((\d{4})-(\d{4})\)', content)
        if years:
            birth_year, death_year = years[0]
            birth_death_info.update({
                'birth_year': int(birth_year),
                'death_year': int(death_year),
                'century': f"{birth_year[:2]}th century" if birth_year.startswith('18') else f"{birth_year[:2]}th century",
                'time_period': 'historical'
            })

    # Extract scientific fields
    field_keywords = {
        'mathematics': ['mathematician', 'algorithm', 'analytical', 'computation'],
        'physics': ['physicist', 'relativity', 'Nobel Prize', 'photoelectric', 'radioactivity'],
        'chemistry': ['chemist', 'chemical', 'elements', 'research'],
        'computer_science': ['computer', 'programming', 'algorithm', 'machine']
    }

    fields = []
    content_lower = content.lower()
    for field, keywords in field_keywords.items():
        if any(keyword in content_lower for keyword in keywords):
            fields.append(field)

    scientist_info['scientific_fields'] = fields
    scientist_info['primary_field'] = fields[0] if fields else 'unknown'

    # Add document quality metrics
    scientist_info.update({
        'word_count': len(content.split()),
        'character_count': len(content),
        'completeness': 'high' if len(content) > 200 else 'medium' if len(content) > 100 else 'low'
    })

    # Merge with existing metadata
    doc.metadata.update(scientist_info)
    return doc

# Apply enhanced metadata extraction
enhanced_documents = []
for doc in raw_documents:
    enhanced_doc = extract_enhanced_metadata(doc)
    enhanced_documents.append(enhanced_doc)

print("\n   Enhanced metadata for each document:")
for doc in enhanced_documents:
    print(f"   📄 {doc.metadata['scientist_name']}:")
    print(f"      • Fields: {', '.join(doc.metadata['scientific_fields'])}")
    print(f"      • Primary: {doc.metadata['primary_field']}")
    print(f"      • Birth year: {doc.metadata.get('birth_year', 'unknown')}")
    print(f"      • Word count: {doc.metadata['word_count']}")

# 2. Text Splitting with Metadata Preservation
print("\n2️⃣ Chunking with metadata preservation:")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100,
    separators=["\n\n", "\n", ". ", " ", ""]
)

chunks = text_splitter.split_documents(enhanced_documents)

# Add chunk-specific metadata
for i, chunk in enumerate(chunks):
    chunk.metadata.update({
        'chunk_id': f"chunk_{i+1}",
        'chunk_size': len(chunk.page_content),
        'chunk_position': 'start' if i < len(chunks) // 3 else 'middle' if i < 2 * len(chunks) // 3 else 'end'
    })

print(f"   Created {len(chunks)} chunks with enhanced metadata")
print("   Sample chunk metadata:")
sample_chunk = chunks[0]
for key, value in sample_chunk.metadata.items():
    print(f"      {key}: {value}")

# 3. Create Vector Store with Rich Metadata
print("\n3️⃣ Building vector store with metadata indexing:")

embeddings = OpenAIEmbeddings()
vector_store = InMemoryVectorStore(embeddings)
vector_store.add_documents(documents=chunks)

print(f"   ✅ Indexed {len(chunks)} chunks with full metadata")

# 4. Metadata Filtering Examples
print("\n4️⃣ Metadata filtering demonstrations:")

# Create filtered retrievers using custom search functions
def search_with_field_filter(query, target_field, k=3):
    """Search with field filtering."""
    all_results = vector_store.similarity_search(query, k=k*3)

    filtered_results = []
    for result in all_results:
        if result.metadata.get('primary_field') == target_field:
            filtered_results.append(result)
        if len(filtered_results) >= k:
            break

    return filtered_results

# Example 1: Field-specific retrieval
print("\n   🔬 Field-specific retrieval (Physics only):")

physics_query = "What are the major scientific contributions?"
physics_results = search_with_field_filter(physics_query, "physics")
print(f"   Query: {physics_query}")
print(f"   Results: {len(physics_results)} physics-related chunks")
for i, result in enumerate(physics_results):
    scientist = result.metadata['scientist_name']
    field = result.metadata['primary_field']
    print(f"   {i+1}. {scientist} ({field}): {result.page_content[:100]}...")

# Example 2: Time period filtering
print("\n   📅 Historical period filtering (19th century):")
def filter_by_century(documents, target_century="19th"):
    """Filter documents by birth century."""
    filtered = []
    for doc in documents:
        birth_year = doc.metadata.get('birth_year')
        if birth_year:
            if target_century == "19th" and 1800 <= birth_year < 1900:
                filtered.append(doc)
    return filtered

# For demonstration, we'll create a custom search
def search_with_time_filter(query, target_century="19th", k=3):
    """Search with time period filtering."""
    # Get all results first
    all_results = vector_store.similarity_search(query, k=k*3)

    # Filter by time period
    filtered_results = []
    for result in all_results:
        birth_year = result.metadata.get('birth_year')
        if birth_year:
            if target_century == "19th" and 1800 <= birth_year < 1900:
                filtered_results.append(result)
        if len(filtered_results) >= k:
            break

    return filtered_results

time_query = "Who made important discoveries?"
time_results = search_with_time_filter(time_query, "19th", k=3)
print(f"   Query: {time_query}")
print(f"   Results: {len(time_results)} 19th century scientists")
for i, result in enumerate(time_results):
    scientist = result.metadata['scientist_name']
    birth_year = result.metadata.get('birth_year', 'unknown')
    print(f"   {i+1}. {scientist} (born {birth_year}): {result.page_content[:100]}...")

# Example 3: Quality-based filtering
print("\n   ⭐ Quality-based filtering (High completeness only):")
def search_with_quality_filter(query, min_completeness="high", k=3):
    """Search with document quality filtering."""
    all_results = vector_store.similarity_search(query, k=k*2)

    filtered_results = []
    for result in all_results:
        if result.metadata.get('completeness') == min_completeness:
            filtered_results.append(result)
        if len(filtered_results) >= k:
            break

    return filtered_results

quality_query = "Tell me about scientific achievements"
quality_results = search_with_quality_filter(quality_query, "high", k=2)
print(f"   Query: {quality_query}")
print(f"   Results: {len(quality_results)} high-quality documents")
for i, result in enumerate(quality_results):
    scientist = result.metadata['scientist_name']
    completeness = result.metadata['completeness']
    word_count = result.metadata['word_count']
    print(f"   {i+1}. {scientist} ({completeness}, {word_count} words): {result.page_content[:100]}...")

# 5. Contextual RAG with Metadata
print("\n5️⃣ Building contextual RAG system:")

llm = ChatOpenAI(model="gpt-5-nano")

# Smart retriever that uses context to determine filters
def create_contextual_retriever(query, k=4):
    """Create a context-aware retriever based on query content."""
    query_lower = query.lower()

    # Determine appropriate filters based on query
    filters = {}

    # Field-specific keywords
    if any(word in query_lower for word in ['physics', 'relativity', 'einstein']):
        filters['primary_field'] = 'physics'
    elif any(word in query_lower for word in ['mathematics', 'algorithm', 'computation']):
        filters['primary_field'] = 'mathematics'
    elif any(word in query_lower for word in ['programming', 'computer', 'lovelace']):
        filters['primary_field'] = 'computer_science'

    # Time-based keywords
    historical_terms = ['historical', 'past', 'old', '19th century', 'early']
    if any(term in query_lower for term in historical_terms):
        # Use custom search for historical filtering
        return search_with_time_filter(query, "19th", k)

    # Quality-based keywords
    if any(word in query_lower for word in ['detailed', 'comprehensive', 'complete']):
        return search_with_quality_filter(query, "high", k)

    # Use filters if determined
    if 'primary_field' in filters:
        return search_with_field_filter(query, filters['primary_field'], k)
    else:
        return vector_store.similarity_search(query, k=k)

# Enhanced prompt that uses metadata
contextual_prompt = ChatPromptTemplate.from_template("""
You are an assistant for question-answering tasks about scientists and their contributions.
Use the following pieces of retrieved context to answer the question.
Pay attention to the metadata information about each source, including:
- The scientist's name and primary field
- Time period and historical context
- Document quality and completeness

If you don't know the answer, just say that you don't know.
Use three sentences maximum and keep the answer concise.

Question: {question}

Context with metadata:
{context}

Answer:
""")

def format_context_with_metadata(retrieved_docs):
    """Format retrieved documents with their metadata for the prompt."""
    formatted_context = []
    for i, doc in enumerate(retrieved_docs):
        metadata = doc.metadata
        scientist = metadata.get('scientist_name', 'Unknown')
        field = metadata.get('primary_field', 'Unknown')
        birth_year = metadata.get('birth_year', 'Unknown')

        context_entry = f"""
Source {i+1}: {scientist} ({field}, born {birth_year})
Content: {doc.page_content}
"""
        formatted_context.append(context_entry)

    return "\n".join(formatted_context)

# Create contextual RAG chain
def contextual_rag_chain(question):
    """RAG chain with contextual retrieval and metadata-aware prompting."""
    # Get contextually relevant documents
    retrieved_docs = create_contextual_retriever(question)

    # Format context with metadata
    formatted_context = format_context_with_metadata(retrieved_docs)

    # Generate response
    response = llm.invoke(
        contextual_prompt.format(
            question=question,
            context=formatted_context
        )
    )

    return response.content, retrieved_docs

# 6. Test Contextual RAG System
print("\n6️⃣ Testing contextual RAG system:")

test_questions = [
    "What physics discoveries were made by Einstein?",
    "Tell me about historical mathematicians and their work",
    "Who worked on early computer programming?",
    "What are the most comprehensive achievements in science?"
]

for i, question in enumerate(test_questions, 1):
    print(f"\n   Q{i}: {question}")
    print("   " + "-" * 50)

    try:
        answer, sources = contextual_rag_chain(question)
        print(f"   A{i}: {answer}")

        print(f"\n   📚 Sources used ({len(sources)} documents):")
        for j, source in enumerate(sources):
            scientist = source.metadata['scientist_name']
            field = source.metadata['primary_field']
            print(f"      {j+1}. {scientist} ({field})")

    except Exception as e:
        print(f"   A{i}: Error - {str(e)}")

# 7. Performance Comparison
print("\n7️⃣ Performance comparison:")

# Test different query types to show filtering effects
comparison_queries = [
    ("What scientific contributions were made?", "Generic query"),
    ("What physics discoveries changed our understanding?", "Physics-specific query"),
    ("Tell me about mathematical breakthroughs", "Mathematics-specific query"),
    ("What are the most comprehensive scientific achievements?", "Quality-focused query")
]

for query, description in comparison_queries:
    print(f"\n   🔍 {description}: {query}")
    print("   " + "=" * 60)

    # Unfiltered retrieval
    unfiltered_results = vector_store.similarity_search(query, k=3)
    print(f"\n   📊 Unfiltered results ({len(unfiltered_results)} documents):")
    for i, result in enumerate(unfiltered_results):
        scientist = result.metadata['scientist_name']
        field = result.metadata['primary_field']
        relevance_preview = result.page_content[:60] + "..."
        print(f"      {i+1}. {scientist} ({field}): {relevance_preview}")

    # Contextually filtered results
    filtered_results = create_contextual_retriever(query, k=3)
    print(f"\n   🎯 Contextually filtered results ({len(filtered_results)} documents):")
    for i, result in enumerate(filtered_results):
        scientist = result.metadata['scientist_name']
        field = result.metadata['primary_field']
        relevance_preview = result.page_content[:60] + "..."
        print(f"      {i+1}. {scientist} ({field}): {relevance_preview}")

    # Show if filtering was applied
    unfiltered_scientists = {r.metadata['scientist_name'] for r in unfiltered_results}
    filtered_scientists = {r.metadata['scientist_name'] for r in filtered_results}

    if unfiltered_scientists != filtered_scientists:
        print(f"   ✅ Filtering effect: Results differ between approaches")
    else:
        print(f"   ➡️ No filtering applied: Generic query returned same results")

    print()

# 8. Metadata Analysis
print("\n8️⃣ Metadata analysis summary:")

# Analyze metadata distribution
field_distribution = {}
birth_year_range = []
quality_distribution = {}

for chunk in chunks:
    # Field distribution
    field = chunk.metadata.get('primary_field', 'unknown')
    field_distribution[field] = field_distribution.get(field, 0) + 1

    # Birth year range
    birth_year = chunk.metadata.get('birth_year')
    if birth_year:
        birth_year_range.append(birth_year)

    # Quality distribution
    quality = chunk.metadata.get('completeness', 'unknown')
    quality_distribution[quality] = quality_distribution.get(quality, 0) + 1

print(f"\n   📈 Metadata Distribution Analysis:")
print(f"   🔬 Scientific Fields:")
for field, count in sorted(field_distribution.items()):
    print(f"      • {field}: {count} chunks")

if birth_year_range:
    print(f"   📅 Time Period Coverage:")
    print(f"      • Earliest: {min(birth_year_range)}")
    print(f"      • Latest: {max(birth_year_range)}")
    print(f"      • Span: {max(birth_year_range) - min(birth_year_range)} years")

print(f"   ⭐ Content Quality:")
for quality, count in sorted(quality_distribution.items()):
    print(f"      • {quality}: {count} chunks")

print(f"\n💡 Contextual RAG system ready with enhanced metadata filtering!")
print(f"🎯 Use contextual_rag_chain('Your question') for intelligent retrieval")