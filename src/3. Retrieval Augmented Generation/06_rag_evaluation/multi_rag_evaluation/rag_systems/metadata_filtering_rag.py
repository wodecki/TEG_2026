import os
import re
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from .base_rag import BaseRAG

class MetadataFilteringRAG(BaseRAG):
    """RAG implementation with enhanced metadata filtering for improved precision."""

    @property
    def name(self) -> str:
        return "Metadata Filtering RAG"

    def _extract_enhanced_metadata(self, doc):
        """Extract rich metadata from document content and filename."""
        source_file = doc.metadata.get('source', '')
        filename = os.path.basename(source_file).replace('.txt', '')
        content = doc.page_content

        scientist_info = {
            'scientist_name': filename,
            'content_type': 'biography',
            'source_type': 'text_file',
            'language': 'english'
        }

        # Extract time periods from content
        if '(' in content and ')' in content:
            years = re.findall(r'\((\d{4})-(\d{4})\)', content)
            if years:
                birth_year, death_year = years[0]
                scientist_info.update({
                    'birth_year': int(birth_year),
                    'death_year': int(death_year),
                    'century': f"{birth_year[:2]}th century",
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

        doc.metadata.update(scientist_info)
        return doc

    def _search_with_metadata_filter(self, query, k=3):
        """Search with smart metadata filtering based on query content."""
        # Get more results initially for filtering
        all_results = self.vector_store.similarity_search(query, k=k*3)

        # Determine relevant field from query
        query_lower = query.lower()
        target_field = None

        if any(word in query_lower for word in ['physics', 'relativity', 'nobel']):
            target_field = 'physics'
        elif any(word in query_lower for word in ['chemistry', 'elements', 'radioactive']):
            target_field = 'chemistry'
        elif any(word in query_lower for word in ['computing', 'programming', 'algorithm']):
            target_field = 'computer_science'
        elif any(word in query_lower for word in ['mathematics', 'mathematical']):
            target_field = 'mathematics'

        # Filter by field if detected, otherwise return top results
        if target_field:
            filtered_results = []
            for result in all_results:
                if result.metadata.get('primary_field') == target_field:
                    filtered_results.append(result)
                if len(filtered_results) >= k:
                    break
            return filtered_results[:k] if filtered_results else all_results[:k]

        return all_results[:k]

    def build(self) -> None:
        """Build metadata-enhanced RAG system."""
        # Enhance chunks with metadata
        enhanced_chunks = []
        for chunk in self.chunks:
            enhanced_chunk = self._extract_enhanced_metadata(chunk)
            enhanced_chunks.append(enhanced_chunk)

        # Build vector store
        embeddings = OpenAIEmbeddings()
        self.vector_store = InMemoryVectorStore(embeddings)
        self.vector_store.add_documents(documents=enhanced_chunks)

        # Create retriever function for the chain
        def metadata_filter_retriever(query):
            return self._search_with_metadata_filter(query, self.config.get("TOP_K", 3))

        self.retriever = metadata_filter_retriever

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