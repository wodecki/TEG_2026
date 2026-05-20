import re
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

try:
    from sentence_transformers import CrossEncoder
except ImportError:
    print("Warning: sentence-transformers not installed. Install with: pip install sentence-transformers")
    CrossEncoder = None

from .base_rag import BaseRAG

class RerankingRAG(BaseRAG):
    """RAG implementation with post-retrieval re-ranking for improved relevance."""

    @property
    def name(self) -> str:
        return "Reranking RAG"

    def _load_cross_encoder(self):
        """Load cross-encoder model for re-ranking."""
        if CrossEncoder is None:
            return None

        try:
            # Use a lightweight cross-encoder model
            return CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        except Exception as e:
            print(f"Warning: Failed to load cross-encoder: {e}")
            return None

    def _cross_encoder_rerank(self, query, documents, top_k=3):
        """Re-rank documents using cross-encoder."""
        if self.cross_encoder is None:
            return documents[:top_k]

        # Prepare query-document pairs
        query_doc_pairs = [(query, doc.page_content) for doc in documents]

        # Get relevance scores
        scores = self.cross_encoder.predict(query_doc_pairs)

        # Sort documents by scores
        doc_score_pairs = list(zip(documents, scores))
        doc_score_pairs.sort(key=lambda x: x[1], reverse=True)

        return [doc for doc, _ in doc_score_pairs[:top_k]]

    def _llm_relevance_scoring(self, query, documents, top_k=3):
        """Use LLM to score document relevance as fallback."""
        relevance_prompt = ChatPromptTemplate.from_template("""
Rate the relevance of the following document to the query on a scale of 1-10.
Consider how well the document answers the question or provides relevant information.

Query: {query}

Document: {document}

Provide only a numeric score (1-10):
""")

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        chain = relevance_prompt | llm | StrOutputParser()

        scored_documents = []

        for doc in documents:
            try:
                result = chain.invoke({
                    "query": query,
                    "document": doc.page_content[:500]  # Limit to avoid long contexts
                })

                # Extract numeric score
                score_match = re.search(r'\b(\d+(?:\.\d+)?)\b', result)
                score = float(score_match.group(1)) if score_match else 5.0

                scored_documents.append((doc, score))

            except Exception as e:
                # Fallback score if LLM fails
                scored_documents.append((doc, 5.0))

        # Sort by score and return top-k
        scored_documents.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in scored_documents[:top_k]]

    def _rerank_documents(self, query, documents, final_k=3):
        """Re-rank documents using available method."""
        if self.cross_encoder is not None:
            return self._cross_encoder_rerank(query, documents, final_k)
        else:
            return self._llm_relevance_scoring(query, documents, final_k)

    def build(self) -> None:
        """Build re-ranking RAG system."""
        # Load cross-encoder for re-ranking
        self.cross_encoder = self._load_cross_encoder()

        # Build vector store
        embeddings = OpenAIEmbeddings()
        self.vector_store = InMemoryVectorStore(embeddings)
        self.vector_store.add_documents(documents=self.chunks)

        # Create retriever function for the chain
        initial_k = self.config.get("RERANK_TOP_K", 6)
        final_k = self.config.get("FINAL_TOP_K", 3)

        def reranking_retriever(query):
            # Get more documents initially
            initial_docs = self.vector_store.similarity_search(query, k=initial_k)
            # Re-rank and return top final_k
            return self._rerank_documents(query, initial_docs, final_k)

        self.retriever = reranking_retriever

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