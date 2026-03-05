"""
Query Expansion for Enhanced Retrieval
======================================

Demonstrates automatic query expansion using LLMs, synonym generation,
and multi-perspective query generation for improved retrieval quality.
"""

from langchain_community.document_loaders import DirectoryLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import re

from dotenv import load_dotenv
load_dotenv(override=True)

print("🔍 QUERY EXPANSION DEMONSTRATION")
print("="*50)

# 1. Load and Prepare Documents
print("\n1️⃣ Loading documents for query expansion:")

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

# 2. Basic Query Expansion Techniques
print("\n2️⃣ Basic query expansion techniques:")

def simple_synonym_expansion(query):
    """Simple synonym-based query expansion."""
    synonyms = {
        'discover': ['find', 'uncover', 'reveal', 'identify'],
        'theory': ['principle', 'law', 'concept', 'hypothesis'],
        'scientist': ['researcher', 'physicist', 'mathematician', 'inventor'],
        'work': ['research', 'study', 'investigation', 'contribution'],
        'famous': ['renowned', 'notable', 'celebrated', 'prominent'],
        'important': ['significant', 'crucial', 'major', 'key']
    }

    expanded_terms = []
    words = query.lower().split()

    for word in words:
        expanded_terms.append(word)
        if word in synonyms:
            expanded_terms.extend(synonyms[word][:2])  # Add top 2 synonyms

    return ' '.join(expanded_terms)

def concept_expansion(query):
    """Expand query with related scientific concepts."""
    concept_map = {
        'einstein': ['relativity', 'photon', 'spacetime', 'mass-energy'],
        'newton': ['gravity', 'motion', 'calculus', 'mechanics'],
        'curie': ['radioactivity', 'radiation', 'polonium', 'radium'],
        'darwin': ['evolution', 'selection', 'species', 'adaptation'],
        'physics': ['mechanics', 'thermodynamics', 'electromagnetism'],
        'mathematics': ['calculus', 'geometry', 'algebra', 'statistics']
    }

    query_lower = query.lower()
    expanded_terms = [query]

    for concept, related_terms in concept_map.items():
        if concept in query_lower:
            # Add top 2 related concepts
            expanded_terms.append(' '.join(related_terms[:2]))

    return ' OR '.join(expanded_terms)

# Test basic expansion
test_query = "Einstein's important discoveries"
print(f"\n   🔍 Original query: {test_query}")
print(f"   📝 Synonym expansion: {simple_synonym_expansion(test_query)}")
print(f"   🧠 Concept expansion: {concept_expansion(test_query)}")

# 3. LLM-Based Query Expansion
print("\n3️⃣ LLM-based query expansion:")

llm = ChatOpenAI(model="gpt-5-nano")

# Query expansion prompts
expansion_prompt = ChatPromptTemplate.from_template("""
You are a search query expert. Given a user's search query, generate an expanded version that includes:
1. Synonyms and related terms
2. More specific scientific terminology
3. Alternative phrasings that might help find relevant information

Original query: {query}

Provide 3 different expanded versions of this query, each focusing on different aspects:
1. Synonym-based expansion
2. Technical term expansion
3. Alternative phrasing expansion

Format your response as:
Synonym: [expanded query]
Technical: [expanded query]
Alternative: [expanded query]
""")

def llm_query_expansion(query):
    """Use LLM to generate expanded queries."""
    try:
        response = llm.invoke(expansion_prompt.format(query=query))
        content = response.content

        # Parse the response
        expansions = {}
        for line in content.split('\n'):
            if line.strip():
                if line.startswith('Synonym:'):
                    expansions['synonym'] = line.replace('Synonym:', '').strip()
                elif line.startswith('Technical:'):
                    expansions['technical'] = line.replace('Technical:', '').strip()
                elif line.startswith('Alternative:'):
                    expansions['alternative'] = line.replace('Alternative:', '').strip()

        return expansions
    except Exception as e:
        print(f"   ⚠️ LLM expansion failed: {e}")
        return {}

# Test LLM expansion
test_queries = [
    "What did Newton discover?",
    "Einstein's theory",
    "Scientific method"
]

for query in test_queries:
    print(f"\n   🔍 Query: {query}")
    expansions = llm_query_expansion(query)
    for expansion_type, expanded_query in expansions.items():
        print(f"   {expansion_type.capitalize()}: {expanded_query}")

# 4. Multi-Perspective Query Generation
print("\n4️⃣ Multi-perspective query generation:")

perspective_prompt = ChatPromptTemplate.from_template("""
Generate 3 different search queries that approach the following topic from different perspectives:

Original topic: {query}

Create queries for these perspectives:
1. Historical perspective (when, where, context)
2. Technical perspective (how, what methods, mechanisms)
3. Impact perspective (why important, consequences, influence)

Format as:
Historical: [query]
Technical: [query]
Impact: [query]
""")

def generate_multi_perspective_queries(query):
    """Generate queries from different perspectives."""
    try:
        response = llm.invoke(perspective_prompt.format(query=query))
        content = response.content

        perspectives = {}
        for line in content.split('\n'):
            if line.strip():
                if line.startswith('Historical:'):
                    perspectives['historical'] = line.replace('Historical:', '').strip()
                elif line.startswith('Technical:'):
                    perspectives['technical'] = line.replace('Technical:', '').strip()
                elif line.startswith('Impact:'):
                    perspectives['impact'] = line.replace('Impact:', '').strip()

        return perspectives
    except Exception as e:
        print(f"   ⚠️ Perspective generation failed: {e}")
        return {}

# Test multi-perspective generation
perspective_topics = [
    "Theory of relativity",
    "Laws of motion",
    "Radioactivity research"
]

for topic in perspective_topics:
    print(f"\n   🎯 Topic: {topic}")
    perspectives = generate_multi_perspective_queries(topic)
    for perspective_type, query in perspectives.items():
        print(f"   {perspective_type.capitalize()}: {query}")

# 5. Context-Aware Query Expansion
print("\n5️⃣ Context-aware query expansion:")

context_prompt = ChatPromptTemplate.from_template("""
You are helping expand search queries for a scientific knowledge base about famous scientists.
The database contains information about: Einstein, Newton, Curie, Darwin, and Lovelace.

Original query: {query}
Available scientists: Einstein (physics), Newton (physics/math), Curie (chemistry/physics), Darwin (biology), Lovelace (computing/math)

Generate an expanded query that:
1. Includes relevant scientist names if applicable
2. Uses appropriate scientific terminology
3. Considers the specific knowledge domain

Expanded query:
""")

def context_aware_expansion(query):
    """Expand query with domain-specific context."""
    try:
        response = llm.invoke(context_prompt.format(query=query))
        return response.content.replace('Expanded query:', '').strip()
    except Exception as e:
        print(f"   ⚠️ Context expansion failed: {e}")
        return query

# Test context-aware expansion
context_queries = [
    "gravity research",
    "computer programming history",
    "radioactive elements",
    "species evolution"
]

for query in context_queries:
    expanded = context_aware_expansion(query)
    print(f"\n   🔍 Original: {query}")
    print(f"   🎯 Context-aware: {expanded}")

# 6. Query Expansion Pipeline
print("\n6️⃣ Query expansion pipeline:")

def query_expansion_pipeline(query, methods=['llm', 'synonym', 'context']):
    """Complete query expansion pipeline."""
    expansions = {'original': query}

    if 'synonym' in methods:
        expansions['synonym'] = simple_synonym_expansion(query)

    if 'concept' in methods:
        expansions['concept'] = concept_expansion(query)

    if 'llm' in methods:
        llm_expansions = llm_query_expansion(query)
        expansions.update(llm_expansions)

    if 'context' in methods:
        expansions['context'] = context_aware_expansion(query)

    if 'perspective' in methods:
        perspectives = generate_multi_perspective_queries(query)
        for key, value in perspectives.items():
            expansions[f'perspective_{key}'] = value

    return expansions

# Test expansion pipeline
pipeline_query = "scientific discoveries"
print(f"\n   🔍 Pipeline test query: {pipeline_query}")

all_expansions = query_expansion_pipeline(
    pipeline_query,
    methods=['llm', 'synonym', 'context', 'perspective']
)

for expansion_type, expanded_query in all_expansions.items():
    print(f"   {expansion_type}: {expanded_query}")

# 7. Retrieval with Query Expansion
print("\n7️⃣ Retrieval comparison with query expansion:")

def search_with_expansion(query, expansion_methods=['original'], k=3):
    """Search using different query expansion methods."""
    # Generate all possible expansions
    expansions = query_expansion_pipeline(query, methods=['llm', 'synonym', 'context'])

    # Collect results for requested methods
    all_results = {}

    for method in expansion_methods:
        if method in expansions:
            expanded_query = expansions[method]
            results = vector_store.similarity_search_with_score(expanded_query, k=k)
            all_results[method] = results

    return all_results

# Test retrieval with different expansions
retrieval_query = "Newton's work"
print(f"\n   🔍 Retrieval test query: {retrieval_query}")

expansion_results = search_with_expansion(
    retrieval_query,
    expansion_methods=['original', 'synonym', 'technical', 'context']
)

for method, results in expansion_results.items():
    print(f"\n   📊 {method.capitalize()} expansion results:")
    for i, (doc, score) in enumerate(results):
        scientist = doc.metadata['scientist_name']
        preview = doc.page_content[:60] + "..."
        print(f"      {i+1}. {scientist} (score: {score:.3f}): {preview}")

# 8. Expanded Query RAG System
print("\n8️⃣ Building expanded query RAG system:")

expansion_rag_prompt = ChatPromptTemplate.from_template("""
You are an assistant for question-answering tasks about scientists and their contributions.
The user's query was expanded to improve retrieval using multiple expansion techniques.
Use the following pieces of retrieved context to answer the question.

Original question: {original_query}
Expanded query used: {expanded_query}

Context: {context}

If you don't know the answer, just say that you don't know.
Use three sentences maximum and keep the answer concise.

Answer:
""")

def expanded_rag_chain(query, expansion_method='context'):
    """RAG chain using query expansion."""
    # Generate expansions
    expansions = query_expansion_pipeline(query, methods=['llm', 'context', 'synonym'])

    # Use specified expansion method
    expanded_query = expansions.get(expansion_method, query)

    # Retrieve documents using expanded query
    results = vector_store.similarity_search(expanded_query, k=4)

    # Format context
    context_parts = []
    for i, doc in enumerate(results):
        scientist = doc.metadata['scientist_name']
        context_parts.append(f"Source {i+1} ({scientist}): {doc.page_content}")

    context = "\n\n".join(context_parts)

    # Generate response
    response = llm.invoke(
        expansion_rag_prompt.format(
            original_query=query,
            expanded_query=expanded_query,
            context=context
        )
    )

    return response.content, expanded_query, results

# 9. Test Expanded RAG System
print("\n9️⃣ Testing expanded RAG system:")

test_questions = [
    "gravity laws",
    "light research",
    "computing pioneers"
]

for i, question in enumerate(test_questions, 1):
    print(f"\n   Q{i}: {question}")
    print("   " + "-" * 50)

    try:
        # Test with different expansion methods
        for method in ['original', 'context', 'technical']:
            if method == 'original':
                # No expansion baseline
                results = vector_store.similarity_search(question, k=4)
                context_parts = []
                for j, doc in enumerate(results):
                    scientist = doc.metadata['scientist_name']
                    context_parts.append(f"Source {j+1} ({scientist}): {doc.page_content}")
                context = "\n\n".join(context_parts)

                response = llm.invoke(
                    expansion_rag_prompt.format(
                        original_query=question,
                        expanded_query=question,
                        context=context
                    )
                )
                answer = response.content
                expanded_query = question
                sources = results
            else:
                answer, expanded_query, sources = expanded_rag_chain(question, method)

            print(f"\n   {method.capitalize()} method:")
            print(f"   Query used: {expanded_query}")
            print(f"   Answer: {answer}")
            print(f"   Sources: {[doc.metadata['scientist_name'] for doc in sources]}")

    except Exception as e:
        print(f"   Error: {str(e)}")

# 10. Expansion Effectiveness Analysis
print("\n🔟 Query expansion effectiveness analysis:")

def analyze_expansion_effectiveness(queries, methods):
    """Analyze how different expansion methods affect retrieval."""
    results_analysis = {}

    for query in queries:
        query_results = {}

        for method in methods:
            if method == 'original':
                search_results = vector_store.similarity_search(query, k=3)
                used_query = query
            else:
                expansions = query_expansion_pipeline(query, methods=[method])
                expanded_query = expansions.get(method, query)
                search_results = vector_store.similarity_search(expanded_query, k=3)
                used_query = expanded_query

            # Analyze diversity of results
            scientists = [doc.metadata['scientist_name'] for doc in search_results]
            unique_scientists = len(set(scientists))

            query_results[method] = {
                'query_used': used_query,
                'unique_scientists': unique_scientists,
                'total_results': len(search_results),
                'scientists': scientists
            }

        results_analysis[query] = query_results

    return results_analysis

# Analyze expansion effectiveness
analysis_queries = ["scientific work", "important discoveries", "physics research"]
analysis_methods = ['original', 'synonym', 'context', 'technical']

effectiveness = analyze_expansion_effectiveness(analysis_queries, analysis_methods)

print(f"\n   📊 Expansion effectiveness analysis:")
print(f"   {'Query':<20} {'Method':<12} {'Unique Sci.':<12} {'Query Length':<12}")
print("   " + "-" * 65)

for query, methods_data in effectiveness.items():
    for method, data in methods_data.items():
        query_len = len(data['query_used'].split())
        unique_count = data['unique_scientists']
        print(f"   {query:<20} {method:<12} {unique_count:<12} {query_len:<12}")

print(f"\n💡 Query expansion RAG system ready!")
print(f"🔍 Use expanded_rag_chain('Your question', 'expansion_method') for enhanced retrieval")
print(f"🎯 Supports: synonym, concept, LLM-based, context-aware, and multi-perspective expansion")