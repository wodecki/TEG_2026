"""
Hybrid Search Implementation
============================

Demonstrates combining semantic similarity with keyword search for improved retrieval.
Shows BM25 + vector search fusion, query routing, and score combination strategies.
"""

from langchain_community.document_loaders import DirectoryLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from rank_bm25 import BM25Okapi
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

from dotenv import load_dotenv
load_dotenv(override=True)

print("🔀 HYBRID SEARCH DEMONSTRATION")
print("="*50)

# 1. Load and Prepare Documents
print("\n1️⃣ Loading documents for hybrid search:")

data_dir = "data/scientists_bios"
loader = DirectoryLoader(data_dir, glob="*.txt")
documents = loader.load()

print(f"   Loaded {len(documents)} documents")

# Add metadata
for doc in documents:
    filename = os.path.basename(doc.metadata['source']).replace('.txt', '')
    doc.metadata.update({
        'scientist_name': filename,
        'word_count': len(doc.page_content.split())
    })

# Chunk documents
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100
)
chunks = text_splitter.split_documents(documents)

print(f"   Created {len(chunks)} chunks for hybrid search")

# 2. Build Multiple Search Indexes
print("\n2️⃣ Building multiple search indexes:")

# Vector search setup
embeddings = OpenAIEmbeddings()
vector_store = InMemoryVectorStore(embeddings)
vector_store.add_documents(documents=chunks)
print(f"   ✅ Vector store: {len(chunks)} chunks embedded")

# BM25 keyword search setup
chunk_texts = [chunk.page_content for chunk in chunks]
tokenized_chunks = [text.lower().split() for text in chunk_texts]
bm25 = BM25Okapi(tokenized_chunks)
print(f"   ✅ BM25 index: {len(chunk_texts)} documents indexed")

# TF-IDF setup for additional keyword matching
tfidf_vectorizer = TfidfVectorizer(
    max_features=1000,
    stop_words='english',
    ngram_range=(1, 2)
)
tfidf_matrix = tfidf_vectorizer.fit_transform(chunk_texts)
print(f"   ✅ TF-IDF index: {tfidf_matrix.shape[1]} features extracted")

# 3. Individual Search Methods
print("\n3️⃣ Testing individual search methods:")

def vector_search(query, k=5):
    """Semantic similarity search using embeddings."""
    results = vector_store.similarity_search_with_score(query, k=k)
    return [(doc, score) for doc, score in results]

def bm25_search(query, k=5):
    """Keyword search using BM25."""
    query_tokens = query.lower().split()
    scores = bm25.get_scores(query_tokens)

    # Get top-k results
    top_indices = np.argsort(scores)[::-1][:k]
    results = []

    for idx in top_indices:
        if scores[idx] > 0:  # Only include non-zero scores
            results.append((chunks[idx], scores[idx]))

    return results

def tfidf_search(query, k=5):
    """TF-IDF based keyword search."""
    query_vec = tfidf_vectorizer.transform([query])
    similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()

    top_indices = np.argsort(similarities)[::-1][:k]
    results = []

    for idx in top_indices:
        if similarities[idx] > 0:
            results.append((chunks[idx], similarities[idx]))

    return results

# Test each method
test_query = "What did Einstein discover about light and energy?"
print(f"\n   🔍 Test query: {test_query}")

print(f"\n   🧠 Vector search results:")
vector_results = vector_search(test_query, k=3)
for i, (doc, score) in enumerate(vector_results):
    scientist = doc.metadata['scientist_name']
    preview = doc.page_content[:80] + "..."
    print(f"      {i+1}. {scientist} (score: {score:.3f}): {preview}")

print(f"\n   🔤 BM25 search results:")
bm25_results = bm25_search(test_query, k=3)
for i, (doc, score) in enumerate(bm25_results):
    scientist = doc.metadata['scientist_name']
    preview = doc.page_content[:80] + "..."
    print(f"      {i+1}. {scientist} (score: {score:.3f}): {preview}")

print(f"\n   📊 TF-IDF search results:")
tfidf_results = tfidf_search(test_query, k=3)
for i, (doc, score) in enumerate(tfidf_results):
    scientist = doc.metadata['scientist_name']
    preview = doc.page_content[:80] + "..."
    print(f"      {i+1}. {scientist} (score: {score:.3f}): {preview}")

# 4. Query Analysis and Routing
print("\n4️⃣ Query analysis and routing:")

def analyze_query(query):
    """Analyze query to determine optimal search strategy."""
    query_lower = query.lower()

    analysis = {
        'has_specific_names': False,
        'has_technical_terms': False,
        'is_conceptual': False,
        'is_factual': False,
        'recommended_strategy': 'hybrid'
    }

    # Check for specific names
    scientist_names = ['einstein', 'newton', 'curie', 'lovelace', 'darwin']
    if any(name in query_lower for name in scientist_names):
        analysis['has_specific_names'] = True

    # Check for technical terms
    technical_terms = ['theory', 'law', 'equation', 'formula', 'discovery', 'invention']
    if any(term in query_lower for term in technical_terms):
        analysis['has_technical_terms'] = True

    # Check for conceptual vs factual
    conceptual_words = ['understand', 'explain', 'concept', 'idea', 'principle']
    factual_words = ['when', 'where', 'what', 'who', 'date', 'year']

    if any(word in query_lower for word in conceptual_words):
        analysis['is_conceptual'] = True
    if any(word in query_lower for word in factual_words):
        analysis['is_factual'] = True

    # Determine strategy
    if analysis['has_specific_names'] and analysis['is_factual']:
        analysis['recommended_strategy'] = 'keyword_heavy'
    elif analysis['is_conceptual']:
        analysis['recommended_strategy'] = 'semantic_heavy'
    else:
        analysis['recommended_strategy'] = 'hybrid'

    return analysis

# Test query analysis
test_queries = [
    "What did Einstein discover?",
    "Explain the concept of gravity",
    "When was Newton born?",
    "How do scientific theories develop?"
]

for query in test_queries:
    analysis = analyze_query(query)
    print(f"\n   📝 Query: {query}")
    print(f"      Strategy: {analysis['recommended_strategy']}")
    print(f"      Has names: {analysis['has_specific_names']}, Technical: {analysis['has_technical_terms']}")
    print(f"      Conceptual: {analysis['is_conceptual']}, Factual: {analysis['is_factual']}")

# 5. Score Fusion Strategies
print("\n5️⃣ Score fusion strategies:")

def normalize_scores(scores, method='min_max'):
    """Normalize scores to 0-1 range."""
    scores = np.array(scores)
    if method == 'min_max':
        min_score, max_score = scores.min(), scores.max()
        if max_score > min_score:
            return (scores - min_score) / (max_score - min_score)
    elif method == 'z_score':
        mean, std = scores.mean(), scores.std()
        if std > 0:
            return (scores - mean) / std
    return scores

def reciprocal_rank_fusion(results_list, k=60):
    """Combine rankings using Reciprocal Rank Fusion."""
    doc_scores = {}

    for results in results_list:
        for rank, (doc, _) in enumerate(results):
            doc_id = id(doc)  # Use object id as unique identifier
            if doc_id not in doc_scores:
                doc_scores[doc_id] = {'doc': doc, 'score': 0}
            doc_scores[doc_id]['score'] += 1 / (k + rank + 1)

    # Sort by combined score
    sorted_results = sorted(doc_scores.values(), key=lambda x: x['score'], reverse=True)
    return [(item['doc'], item['score']) for item in sorted_results]

def weighted_score_fusion(vector_results, keyword_results, vector_weight=0.6):
    """Combine results using weighted score fusion."""
    # Normalize scores
    vector_scores = [score for _, score in vector_results]
    keyword_scores = [score for _, score in keyword_results]

    norm_vector_scores = normalize_scores(vector_scores)
    norm_keyword_scores = normalize_scores(keyword_scores)

    # Create combined results
    doc_scores = {}

    # Add vector results
    for i, (doc, _) in enumerate(vector_results):
        doc_id = id(doc)
        doc_scores[doc_id] = {
            'doc': doc,
            'vector_score': norm_vector_scores[i],
            'keyword_score': 0
        }

    # Add keyword results
    for i, (doc, _) in enumerate(keyword_results):
        doc_id = id(doc)
        if doc_id in doc_scores:
            doc_scores[doc_id]['keyword_score'] = norm_keyword_scores[i]
        else:
            doc_scores[doc_id] = {
                'doc': doc,
                'vector_score': 0,
                'keyword_score': norm_keyword_scores[i]
            }

    # Calculate combined scores
    for doc_id in doc_scores:
        doc_scores[doc_id]['combined_score'] = (
            vector_weight * doc_scores[doc_id]['vector_score'] +
            (1 - vector_weight) * doc_scores[doc_id]['keyword_score']
        )

    # Sort by combined score
    sorted_results = sorted(doc_scores.values(), key=lambda x: x['combined_score'], reverse=True)
    return [(item['doc'], item['combined_score']) for item in sorted_results]

# Test fusion strategies
fusion_query = "Einstein's theory of relativity and light"
print(f"\n   🔍 Fusion test query: {fusion_query}")

vector_results = vector_search(fusion_query, k=5)
bm25_results = bm25_search(fusion_query, k=5)

print(f"\n   🔗 Reciprocal Rank Fusion:")
rrf_results = reciprocal_rank_fusion([vector_results, bm25_results])
for i, (doc, score) in enumerate(rrf_results[:3]):
    scientist = doc.metadata['scientist_name']
    preview = doc.page_content[:60] + "..."
    print(f"      {i+1}. {scientist} (RRF: {score:.3f}): {preview}")

print(f"\n   ⚖️ Weighted Score Fusion (60% vector, 40% keyword):")
wsf_results = weighted_score_fusion(vector_results, bm25_results, vector_weight=0.6)
for i, (doc, score) in enumerate(wsf_results[:3]):
    scientist = doc.metadata['scientist_name']
    preview = doc.page_content[:60] + "..."
    print(f"      {i+1}. {scientist} (WSF: {score:.3f}): {preview}")

# 6. Adaptive Hybrid Search
print("\n6️⃣ Adaptive hybrid search:")

def adaptive_hybrid_search(query, k=5):
    """Adaptive search that adjusts strategy based on query analysis."""
    analysis = analyze_query(query)

    # Get results from both methods
    vector_results = vector_search(query, k=k*2)
    bm25_results = bm25_search(query, k=k*2)

    # Adjust weights based on query type
    if analysis['recommended_strategy'] == 'semantic_heavy':
        vector_weight = 0.8
    elif analysis['recommended_strategy'] == 'keyword_heavy':
        vector_weight = 0.3
    else:  # hybrid
        vector_weight = 0.6

    # Use weighted fusion
    results = weighted_score_fusion(vector_results, bm25_results, vector_weight)
    return results[:k], analysis

# Test adaptive search
adaptive_queries = [
    "What is Einstein famous for?",  # keyword_heavy (specific name + factual)
    "Explain scientific methodology",  # semantic_heavy (conceptual)
    "How did Newton contribute to physics?"  # hybrid
]

for query in adaptive_queries:
    print(f"\n   🔍 Query: {query}")
    results, analysis = adaptive_hybrid_search(query, k=3)
    strategy = analysis['recommended_strategy']
    print(f"   📊 Strategy: {strategy}")

    for i, (doc, score) in enumerate(results):
        scientist = doc.metadata['scientist_name']
        preview = doc.page_content[:70] + "..."
        print(f"      {i+1}. {scientist} (score: {score:.3f}): {preview}")

# 7. Hybrid RAG System
print("\n7️⃣ Building hybrid RAG system:")

llm = ChatOpenAI(model="gpt-5-nano")

hybrid_prompt = ChatPromptTemplate.from_template("""
You are an assistant for question-answering tasks about scientists and their contributions.
Use the following pieces of retrieved context to answer the question.
The context was retrieved using hybrid search combining semantic similarity and keyword matching.

If you don't know the answer, just say that you don't know.
Use three sentences maximum and keep the answer concise.

Question: {question}

Context: {context}

Answer:
""")

def hybrid_rag_chain(question):
    """RAG chain using adaptive hybrid search."""
    # Get hybrid search results
    results, analysis = adaptive_hybrid_search(question, k=4)

    # Format context
    context_parts = []
    for i, (doc, score) in enumerate(results):
        scientist = doc.metadata['scientist_name']
        context_parts.append(f"Source {i+1} ({scientist}): {doc.page_content}")

    context = "\n\n".join(context_parts)

    # Generate response
    response = llm.invoke(
        hybrid_prompt.format(question=question, context=context)
    )

    return response.content, results, analysis

# 8. Test Hybrid RAG
print("\n8️⃣ Testing hybrid RAG system:")

test_questions = [
    "What specific discoveries did Einstein make?",
    "How do scientific theories get developed?",
    "When did Newton live and what did he study?"
]

for i, question in enumerate(test_questions, 1):
    print(f"\n   Q{i}: {question}")
    print("   " + "-" * 50)

    try:
        answer, sources, analysis = hybrid_rag_chain(question)
        print(f"   A{i}: {answer}")

        print(f"\n   📊 Search strategy: {analysis['recommended_strategy']}")
        print(f"   📚 Sources ({len(sources)} documents):")
        for j, (source, score) in enumerate(sources):
            scientist = source.metadata['scientist_name']
            print(f"      {j+1}. {scientist} (score: {score:.3f})")

    except Exception as e:
        print(f"   A{i}: Error - {str(e)}")

# 9. Performance Analysis
print("\n9️⃣ Hybrid search performance analysis:")

# Compare different approaches on various query types
comparison_queries = [
    ("Einstein relativity", "Factual with name"),
    ("scientific discovery process", "Conceptual general"),
    ("Newton apple gravity story", "Specific narrative"),
    ("physics principles", "General conceptual")
]

print(f"\n   📊 Method comparison across query types:")
print(f"   {'Query Type':<20} {'Vector':<8} {'BM25':<8} {'Hybrid':<8}")
print("   " + "-" * 50)

for query, query_type in comparison_queries:
    # Get results from each method
    vector_res = vector_search(query, k=3)
    bm25_res = bm25_search(query, k=3)
    hybrid_res, _ = adaptive_hybrid_search(query, k=3)

    # Count unique scientists in top 3
    vector_scientists = len(set(doc.metadata['scientist_name'] for doc, _ in vector_res))
    bm25_scientists = len(set(doc.metadata['scientist_name'] for doc, _ in bm25_res))
    hybrid_scientists = len(set(doc.metadata['scientist_name'] for doc, _ in hybrid_res))

    print(f"   {query_type:<20} {vector_scientists:<8} {bm25_scientists:<8} {hybrid_scientists:<8}")

print(f"\n💡 Hybrid RAG system ready with adaptive search strategies!")
print(f"🔀 Use hybrid_rag_chain('Your question') for intelligent hybrid retrieval")
print(f"📊 Combines semantic similarity + keyword matching + adaptive weighting")