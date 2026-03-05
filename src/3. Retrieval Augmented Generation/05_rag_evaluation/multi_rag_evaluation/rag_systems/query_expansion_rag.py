from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from .base_rag import BaseRAG

class QueryExpansionRAG(BaseRAG):
    """RAG implementation with query expansion for improved retrieval coverage."""

    @property
    def name(self) -> str:
        return "Query Expansion RAG"

    def _expand_query_with_llm(self, query):
        """Expand query using LLM to generate alternative phrasings."""
        expansion_prompt = ChatPromptTemplate.from_template("""
You are a search query expert. Given a user's search query about scientists and their work,
generate {max_variations} alternative versions that might help find relevant information.

Focus on:
1. Synonyms and related terms
2. More specific scientific terminology
3. Alternative phrasings

Original query: {query}

Return only the alternative queries, one per line, without numbering or explanation:
""")

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
        chain = expansion_prompt | llm | StrOutputParser()

        max_variations = self.config.get("MAX_QUERY_VARIATIONS", 3)
        result = chain.invoke({
            "query": query,
            "max_variations": max_variations
        })

        # Parse the variations
        variations = [line.strip() for line in result.split('\n') if line.strip()]
        return [query] + variations[:max_variations]

    def _simple_concept_expansion(self, query):
        """Add domain-specific terms based on query content."""
        concept_map = {
            'einstein': ['relativity', 'photon', 'spacetime'],
            'newton': ['gravity', 'motion', 'calculus'],
            'curie': ['radioactivity', 'radiation', 'polonium'],
            'darwin': ['evolution', 'selection', 'species'],
            'lovelace': ['programming', 'algorithm', 'computer']
        }

        query_lower = query.lower()
        expanded_terms = []

        for scientist, concepts in concept_map.items():
            if scientist in query_lower:
                expanded_terms.extend(concepts[:2])

        if expanded_terms:
            return f"{query} {' '.join(expanded_terms)}"
        return query

    def _multi_query_search(self, query, k=3):
        """Perform search with multiple query variations and combine results."""
        # Generate query variations
        query_variations = self._expand_query_with_llm(query)

        # Add simple concept expansion
        concept_expanded = self._simple_concept_expansion(query)
        if concept_expanded != query:
            query_variations.append(concept_expanded)

        # Search with each variation
        all_results = []
        seen_docs = set()

        for variation in query_variations:
            results = self.vector_store.similarity_search(variation, k=k*2)
            for doc in results:
                doc_id = id(doc)
                if doc_id not in seen_docs:
                    all_results.append(doc)
                    seen_docs.add(doc_id)

        # Return top-k unique results
        return all_results[:k]

    def build(self) -> None:
        """Build query expansion RAG system."""
        # Build vector store
        embeddings = OpenAIEmbeddings()
        self.vector_store = InMemoryVectorStore(embeddings)
        self.vector_store.add_documents(documents=self.chunks)

        # Create retriever function for the chain
        def query_expansion_retriever(query):
            return self._multi_query_search(query, self.config.get("TOP_K", 3))

        self.retriever = query_expansion_retriever

        llm = ChatOpenAI(model=self.config.get("RAG_MODEL", "gpt-4o-mini"))

        prompt = ChatPromptTemplate.from_template("""
You are an assistant for question-answering tasks.
Use the following pieces of retrieved context to answer the question.
If you don't know the answer, just say that you don't know.
Use three sentences maximum and keep the answer concise.

Question: {question}

Context: {context}

Answer:
""")

        self.rag_chain = (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )