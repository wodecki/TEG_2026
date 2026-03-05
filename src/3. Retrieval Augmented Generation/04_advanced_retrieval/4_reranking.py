"""
Re-ranking for Post-Retrieval Optimization
==========================================

Demonstrates cross-encoder re-ranking, LLM-based scoring, and result optimization
techniques to improve retrieval quality after initial search.
"""

from langchain_community.document_loaders import DirectoryLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import CrossEncoder
import numpy as np
import os
import time

from dotenv import load_dotenv
load_dotenv(override=True)

print("🎯 RE-RANKING DEMONSTRATION")
print("="*50)

# 1. Load and Prepare Documents
print("\n1️⃣ Loading documents for re-ranking:")

data_dir = "data/scientists_bios"
loader = DirectoryLoader(data_dir, glob="*.txt")
documents = loader.load()

# Add metadata
for doc in documents:
    filename = os.path.basename(doc.metadata['source']).replace('.txt', '')
    doc.metadata['scientist_name'] = filename

# Chunk documents
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100
)
chunks = text_splitter.split_documents(documents)

print(f"   Loaded {len(documents)} documents, created {len(chunks)} chunks")

# Build vector store
embeddings = OpenAIEmbeddings()
vector_store = InMemoryVectorStore(embeddings)
vector_store.add_documents(documents=chunks)

print(f"   ✅ Vector store ready with {len(chunks)} indexed chunks")

# 2. Load Cross-Encoder Models
print("\n2️⃣ Loading cross-encoder models for re-ranking:")

# Load different cross-encoder models for comparison
cross_encoders = {}

try:
    # Lightweight cross-encoder for general ranking
    cross_encoders['ms-marco'] = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    print("   ✅ MS-MARCO MiniLM cross-encoder loaded")
except Exception as e:
    print(f"   ⚠️ Failed to load MS-MARCO model: {e}")

try:
    # More specific cross-encoder for question-answering
    cross_encoders['qnli'] = CrossEncoder('cross-encoder/qnli-electra-base')
    print("   ✅ QNLI Electra cross-encoder loaded")
except Exception as e:
    print(f"   ⚠️ Failed to load QNLI model: {e}")

if not cross_encoders:
    print("   ⚠️ No cross-encoders loaded, using fallback scoring")

# 3. Basic Re-ranking Functions
print("\n3️⃣ Implementing re-ranking functions:")

def cross_encoder_rerank(query, documents, model_name='ms-marco', top_k=None):
    """Re-rank documents using cross-encoder models."""
    if model_name not in cross_encoders:
        print(f"   ⚠️ Model {model_name} not available, returning original order")
        return documents

    model = cross_encoders[model_name]

    # Prepare query-document pairs
    query_doc_pairs = [(query, doc.page_content) for doc in documents]

    # Get relevance scores
    scores = model.predict(query_doc_pairs)

    # Sort documents by scores
    doc_score_pairs = list(zip(documents, scores))
    doc_score_pairs.sort(key=lambda x: x[1], reverse=True)

    # Return top_k or all documents
    if top_k:
        return doc_score_pairs[:top_k]
    else:
        return doc_score_pairs

def llm_relevance_scoring(query, documents, llm):
    """Use LLM to score document relevance."""
    relevance_prompt = ChatPromptTemplate.from_template("""
Rate the relevance of the following document to the query on a scale of 1-10.
Consider how well the document answers the question or provides relevant information.

Query: {query}

Document: {document}

Provide only a numeric score (1-10) with brief explanation:
Score: [number]
Reason: [brief explanation]
""")

    scored_documents = []

    for doc in documents:
        try:
            response = llm.invoke(
                relevance_prompt.format(
                    query=query,
                    document=doc.page_content[:500]  # Limit content for efficiency
                )
            )

            # Extract score from response
            content = response.content
            score_line = [line for line in content.split('\n') if line.startswith('Score:')]

            if score_line:
                score_text = score_line[0].replace('Score:', '').strip()
                try:
                    score = float(score_text.split()[0])  # Take first number
                    scored_documents.append((doc, score))
                except:
                    scored_documents.append((doc, 5.0))  # Default score
            else:
                scored_documents.append((doc, 5.0))  # Default score

        except Exception as e:
            print(f"   ⚠️ LLM scoring failed for document: {e}")
            scored_documents.append((doc, 5.0))  # Default score

    # Sort by score
    scored_documents.sort(key=lambda x: x[1], reverse=True)
    return scored_documents

def diversity_rerank(documents, diversity_threshold=0.7):
    """Re-rank to promote diversity while maintaining relevance."""
    if not documents:
        return documents

    # Start with highest scoring document
    diverse_docs = [documents[0]]
    remaining_docs = documents[1:]

    # Simple diversity based on scientist names
    selected_scientists = {documents[0][0].metadata['scientist_name']}

    for doc, score in remaining_docs:
        scientist = doc.metadata['scientist_name']

        # Add document if it's from a new scientist or if we have room
        if scientist not in selected_scientists or len(diverse_docs) < 3:
            diverse_docs.append((doc, score))
            selected_scientists.add(scientist)

        # Stop if we have enough diverse results
        if len(diverse_docs) >= len(documents) * 0.8:  # Take 80% of results
            break

    # Add remaining high-scoring documents
    for doc, score in remaining_docs:
        if (doc, score) not in diverse_docs and len(diverse_docs) < len(documents):
            diverse_docs.append((doc, score))

    return diverse_docs

# 4. Test Individual Re-ranking Methods
print("\n4️⃣ Testing individual re-ranking methods:")

# Get initial results for testing
test_query = "What did Einstein discover about the universe?"
initial_results = vector_store.similarity_search_with_score(test_query, k=6)

print(f"\n   🔍 Test query: {test_query}")
print(f"\n   📊 Initial vector search results:")
for i, (doc, score) in enumerate(initial_results):
    scientist = doc.metadata['scientist_name']
    preview = doc.page_content[:60] + "..."
    print(f"      {i+1}. {scientist} (score: {score:.3f}): {preview}")

# Test cross-encoder re-ranking
if cross_encoders:
    print(f"\n   🎯 Cross-encoder re-ranking:")
    documents_only = [doc for doc, score in initial_results]

    for model_name in cross_encoders:
        reranked = cross_encoder_rerank(test_query, documents_only, model_name, top_k=4)
        print(f"\n   {model_name.upper()} re-ranking:")
        for i, (doc, score) in enumerate(reranked):
            scientist = doc.metadata['scientist_name']
            preview = doc.page_content[:60] + "..."
            print(f"      {i+1}. {scientist} (score: {score:.3f}): {preview}")

# Test LLM re-ranking
llm = ChatOpenAI(model="gpt-5-nano")
print(f"\n   🤖 LLM relevance scoring:")
llm_reranked = llm_relevance_scoring(test_query, documents_only[:4], llm)
for i, (doc, score) in enumerate(llm_reranked):
    scientist = doc.metadata['scientist_name']
    preview = doc.page_content[:60] + "..."
    print(f"      {i+1}. {scientist} (score: {score:.1f}): {preview}")

# Test diversity re-ranking
print(f"\n   🌈 Diversity re-ranking:")
diverse_reranked = diversity_rerank(initial_results[:6])
for i, (doc, score) in enumerate(diverse_reranked):
    scientist = doc.metadata['scientist_name']
    preview = doc.page_content[:60] + "..."
    print(f"      {i+1}. {scientist} (orig score: {score:.3f}): {preview}")

# 5. Ensemble Re-ranking
print("\n5️⃣ Ensemble re-ranking:")

def ensemble_rerank(query, documents, methods=['cross_encoder', 'llm'], weights=None):
    """Combine multiple re-ranking methods."""
    if weights is None:
        weights = [1.0] * len(methods)

    # Normalize weights
    total_weight = sum(weights)
    weights = [w / total_weight for w in weights]

    # Store scores for each method as lists
    all_method_scores = []

    for method in methods:
        if method == 'cross_encoder' and cross_encoders:
            model_name = list(cross_encoders.keys())[0]  # Use first available
            reranked = cross_encoder_rerank(query, documents, model_name)
            # Create score list in same order as documents
            scores = []
            reranked_dict = {doc.page_content: score for doc, score in reranked}
            for doc in documents:
                scores.append(reranked_dict.get(doc.page_content, 0))
            all_method_scores.append(scores)

        elif method == 'llm':
            reranked = llm_relevance_scoring(query, documents[:len(documents)], llm)
            # Normalize LLM scores to 0-1 range
            max_score = max(score for _, score in reranked) if reranked else 10
            scores = []
            reranked_dict = {doc.page_content: score/max_score for doc, score in reranked}
            for doc in documents:
                scores.append(reranked_dict.get(doc.page_content, 0))
            all_method_scores.append(scores)

    # Combine scores
    final_scores = []
    for i, doc in enumerate(documents):
        combined_score = 0
        for j, method_scores in enumerate(all_method_scores):
            if i < len(method_scores):
                combined_score += weights[j] * method_scores[i]
        final_scores.append((doc, combined_score))

    # Sort by combined scores
    final_scores.sort(key=lambda x: x[1], reverse=True)
    return final_scores

# Test ensemble re-ranking
ensemble_methods = ['llm']
if cross_encoders:
    ensemble_methods.append('cross_encoder')

print(f"\n   🎭 Ensemble re-ranking (methods: {ensemble_methods}):")
ensemble_reranked = ensemble_rerank(
    test_query,
    documents_only[:5],
    methods=ensemble_methods,
    weights=[0.6, 0.4] if len(ensemble_methods) > 1 else [1.0]
)

for i, (doc, score) in enumerate(ensemble_reranked):
    scientist = doc.metadata['scientist_name']
    preview = doc.page_content[:60] + "..."
    print(f"      {i+1}. {scientist} (ensemble: {score:.3f}): {preview}")

# 6. Performance vs Quality Analysis
print("\n6️⃣ Performance vs quality analysis:")

def benchmark_reranking_methods(queries, k=5):
    """Benchmark different re-ranking methods."""
    methods = ['baseline', 'llm']
    if cross_encoders:
        methods.append('cross_encoder')

    results = {method: {'total_time': 0, 'queries_processed': 0} for method in methods}

    for query in queries:
        # Get initial results
        initial_docs = vector_store.similarity_search(query, k=k*2)

        for method in methods:
            start_time = time.time()

            if method == 'baseline':
                # No re-ranking, just return initial results
                final_docs = initial_docs[:k]

            elif method == 'cross_encoder' and cross_encoders:
                model_name = list(cross_encoders.keys())[0]
                reranked = cross_encoder_rerank(query, initial_docs, model_name, top_k=k)
                final_docs = [doc for doc, score in reranked]

            elif method == 'llm':
                reranked = llm_relevance_scoring(query, initial_docs[:k], llm)
                final_docs = [doc for doc, score in reranked]

            end_time = time.time()
            processing_time = end_time - start_time

            results[method]['total_time'] += processing_time
            results[method]['queries_processed'] += 1

    return results

# Run benchmark
benchmark_queries = [
    "Einstein's theories",
    "Newton's discoveries",
    "Marie Curie research"
]

print(f"\n   ⏱️ Benchmarking re-ranking methods:")
benchmark_results = benchmark_reranking_methods(benchmark_queries, k=3)

print(f"   {'Method':<15} {'Avg Time (s)':<15} {'Queries':<10}")
print("   " + "-" * 45)

for method, data in benchmark_results.items():
    avg_time = data['total_time'] / data['queries_processed'] if data['queries_processed'] > 0 else 0
    print(f"   {method:<15} {avg_time:<15.3f} {data['queries_processed']:<10}")

# 7. Re-ranking RAG System
print("\n7️⃣ Building re-ranking RAG system:")

rerank_rag_prompt = ChatPromptTemplate.from_template("""
You are an assistant for question-answering tasks about scientists and their contributions.
The context below was retrieved and then re-ranked to ensure the most relevant information appears first.

Use the following pieces of re-ranked context to answer the question.
If you don't know the answer, just say that you don't know.
Use three sentences maximum and keep the answer concise.

Question: {question}

Re-ranked context: {context}

Answer:
""")

def reranking_rag_chain(query, rerank_method='llm', k=4):
    """RAG chain with re-ranking."""
    # Get initial results (more than needed)
    initial_results = vector_store.similarity_search(query, k=k*2)

    # Apply re-ranking
    if rerank_method == 'cross_encoder' and cross_encoders:
        model_name = list(cross_encoders.keys())[0]
        reranked = cross_encoder_rerank(query, initial_results, model_name, top_k=k)
        final_docs = [doc for doc, score in reranked]
        scores = [score for doc, score in reranked]

    elif rerank_method == 'llm':
        reranked = llm_relevance_scoring(query, initial_results[:k+2], llm)
        final_docs = [doc for doc, score in reranked[:k]]
        scores = [score for doc, score in reranked[:k]]

    elif rerank_method == 'ensemble':
        ensemble_methods = ['llm']
        if cross_encoders:
            ensemble_methods.append('cross_encoder')
        reranked = ensemble_rerank(query, initial_results[:k+2], methods=ensemble_methods)
        final_docs = [doc for doc, score in reranked[:k]]
        scores = [score for doc, score in reranked[:k]]

    else:  # baseline
        final_docs = initial_results[:k]
        scores = [1.0] * len(final_docs)  # Dummy scores

    # Format context
    context_parts = []
    for i, doc in enumerate(final_docs):
        scientist = doc.metadata['scientist_name']
        context_parts.append(f"Source {i+1} ({scientist}): {doc.page_content}")

    context = "\n\n".join(context_parts)

    # Generate response
    response = llm.invoke(
        rerank_rag_prompt.format(question=query, context=context)
    )

    return response.content, final_docs, scores

# 8. Test Re-ranking RAG System
print("\n8️⃣ Testing re-ranking RAG system:")

test_questions = [
    "What are Einstein's most important contributions?",
    "How did Newton change physics?",
    "What did Marie Curie discover?"
]

for i, question in enumerate(test_questions, 1):
    print(f"\n   Q{i}: {question}")
    print("   " + "-" * 50)

    try:
        # Test different re-ranking methods
        methods_to_test = ['baseline', 'llm']
        if cross_encoders:
            methods_to_test.append('cross_encoder')

        for method in methods_to_test:
            answer, sources, scores = reranking_rag_chain(question, method)

            print(f"\n   {method.capitalize()} re-ranking:")
            print(f"   Answer: {answer}")
            print(f"   Sources: {[doc.metadata['scientist_name'] for doc in sources]}")
            if method != 'baseline':
                print(f"   Scores: {[f'{score:.2f}' for score in scores]}")

    except Exception as e:
        print(f"   Error: {str(e)}")

# 9. Re-ranking Effectiveness Analysis
print("\n9️⃣ Re-ranking effectiveness analysis:")

def analyze_reranking_effectiveness(queries, methods):
    """Analyze how re-ranking affects result quality."""
    effectiveness_data = {}

    for query in queries:
        query_data = {}

        # Get baseline results
        baseline_docs = vector_store.similarity_search(query, k=5)

        for method in methods:
            if method == 'baseline':
                final_docs = baseline_docs
                scientists = [doc.metadata['scientist_name'] for doc in final_docs]

            elif method == 'llm':
                reranked = llm_relevance_scoring(query, baseline_docs, llm)
                final_docs = [doc for doc, score in reranked]
                scientists = [doc.metadata['scientist_name'] for doc in final_docs]

            elif method == 'cross_encoder' and cross_encoders:
                model_name = list(cross_encoders.keys())[0]
                reranked = cross_encoder_rerank(query, baseline_docs, model_name)
                final_docs = [doc for doc, score in reranked]
                scientists = [doc.metadata['scientist_name'] for doc in final_docs]

            else:
                continue

            # Analyze diversity and relevance
            unique_scientists = len(set(scientists))
            total_docs = len(final_docs)

            query_data[method] = {
                'unique_scientists': unique_scientists,
                'total_docs': total_docs,
                'diversity_ratio': unique_scientists / total_docs if total_docs > 0 else 0
            }

        effectiveness_data[query] = query_data

    return effectiveness_data

# Analyze effectiveness
analysis_queries = ["Einstein relativity", "Newton gravity", "Curie radioactivity"]
analysis_methods = ['baseline', 'llm']
if cross_encoders:
    analysis_methods.append('cross_encoder')

effectiveness = analyze_reranking_effectiveness(analysis_queries, analysis_methods)

print(f"\n   📊 Re-ranking effectiveness analysis:")
print(f"   {'Query':<20} {'Method':<15} {'Unique Sci.':<12} {'Diversity':<12}")
print("   " + "-" * 65)

for query, methods_data in effectiveness.items():
    for method, data in methods_data.items():
        unique_count = data['unique_scientists']
        diversity = data['diversity_ratio']
        print(f"   {query:<20} {method:<15} {unique_count:<12} {diversity:<12.2f}")

print(f"\n💡 Re-ranking RAG system ready!")
print(f"🎯 Use reranking_rag_chain('Your question', 'method') for optimized retrieval")

available_methods = ['baseline', 'llm']
if cross_encoders:
    available_methods.extend(['cross_encoder', 'ensemble'])

print(f"🔄 Available methods: {', '.join(available_methods)}")