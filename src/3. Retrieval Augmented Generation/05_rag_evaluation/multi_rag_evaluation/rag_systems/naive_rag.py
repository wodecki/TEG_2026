from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from .base_rag import BaseRAG

class NaiveRAG(BaseRAG):
    """Basic RAG implementation using simple vector similarity search."""

    @property
    def name(self) -> str:
        return "Naive RAG"

    def build(self) -> None:
        """Build basic RAG system with vector store and simple retrieval."""
        embeddings = OpenAIEmbeddings()
        vector_store = InMemoryVectorStore(embeddings)
        vector_store.add_documents(documents=self.chunks)

        self.retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": self.config.get("TOP_K", 3)}
        )

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