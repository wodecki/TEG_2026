import numpy as np
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

try:
    from rank_bm25 import BM25Okapi
except ImportError:
    print("Warning: rank_bm25 not installed. Install with: pip install rank-bm25")
    BM25Okapi = None

from .base_rag import BaseRAG

class HybridSearchRAG(BaseRAG):
    """RAG implementation combining BM25 keyword search with vector similarity."""

    @property
    def name(self) -> str:
        return "Hybrid Search RAG"

    def _build_bm25_index(self):
        """Build BM25 index for keyword search."""
        if BM25Okapi is None:
            raise ImportError("rank_bm25 package required for hybrid search")

        chunk_texts = [chunk.page_content for chunk in self.chunks]
        tokenized_chunks = [text.lower().split() for text in chunk_texts]
        return BM25Okapi(tokenized_chunks)

    def _bm25_search(self, query, k=5):
        """Perform BM25 keyword search."""
        query_tokens = query.lower().split()
        scores = self.bm25.get_scores(query_tokens)

        top_indices = np.argsort(scores)[::-1][:k]
        results = []

        for idx in top_indices:
            if scores[idx] > 0:
                results.append((self.chunks[idx], scores[idx]))

        return results

    def _vector_search(self, query, k=5):
        """Perform vector similarity search."""
        results = self.vector_store.similarity_search_with_score(query, k=k)
        return [(doc, score) for doc, score in results]

    def _hybrid_search(self, query, k=3):
        """Combine BM25 and vector search results."""
        # Get results from both methods
        bm25_results = self._bm25_search(query, k=k*2)
        vector_results = self._vector_search(query, k=k*2)

        # Normalize scores
        def normalize_scores(results):
            if not results:
                return []
            scores = [score for _, score in results]
            min_score, max_score = min(scores), max(scores)
            if max_score == min_score:
                return [(doc, 1.0) for doc, _ in results]
            return [(doc, (score - min_score) / (max_score - min_score))
                   for doc, score in results]

        norm_bm25 = normalize_scores(bm25_results)
        norm_vector = normalize_scores(vector_results)

        # Combine scores with weights
        combined_scores = {}
        bm25_weight = self.config.get("BM25_WEIGHT", 0.3)
        vector_weight = 1.0 - bm25_weight

        for doc, score in norm_bm25:
            doc_id = id(doc)
            combined_scores[doc_id] = combined_scores.get(doc_id, 0) + score * bm25_weight

        for doc, score in norm_vector:
            doc_id = id(doc)
            combined_scores[doc_id] = combined_scores.get(doc_id, 0) + score * vector_weight

        # Create document mapping
        doc_mapping = {}
        for doc, _ in bm25_results + vector_results:
            doc_mapping[id(doc)] = doc

        # Sort by combined score and return top-k
        sorted_results = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)

        final_results = []
        for doc_id, score in sorted_results[:k]:
            if doc_id in doc_mapping:
                final_results.append(doc_mapping[doc_id])

        return final_results

    def build(self) -> None:
        """Build hybrid search RAG system."""
        # Build vector store
        embeddings = OpenAIEmbeddings()
        self.vector_store = InMemoryVectorStore(embeddings)
        self.vector_store.add_documents(documents=self.chunks)

        # Build BM25 index
        self.bm25 = self._build_bm25_index()

        # Create retriever function for the chain
        def hybrid_retriever(query):
            return self._hybrid_search(query, self.config.get("TOP_K", 3))

        self.retriever = hybrid_retriever

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