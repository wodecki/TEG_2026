from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any

class BaseRAG(ABC):
    """Abstract base class for all RAG implementations."""

    def __init__(self, chunks: List, config: Dict[str, Any]):
        self.chunks = chunks
        self.config = config
        self.rag_chain = None
        self.retriever = None

    @abstractmethod
    def build(self) -> None:
        """Build the RAG system components."""
        pass

    def query(self, question: str) -> Tuple[str, List[str]]:
        """Query the RAG system and return answer with contexts."""
        if not self.rag_chain or not self.retriever:
            raise RuntimeError(f"{self.name} not built. Call build() first.")

        answer = self.rag_chain.invoke(question)

        # Handle both function and object retrievers
        if callable(self.retriever):
            retrieved_docs = self.retriever(question)
        else:
            retrieved_docs = self.retriever.invoke(question)

        contexts = [doc.page_content for doc in retrieved_docs]
        return answer, contexts

    @property
    @abstractmethod
    def name(self) -> str:
        """Return descriptive name for this RAG system."""
        pass