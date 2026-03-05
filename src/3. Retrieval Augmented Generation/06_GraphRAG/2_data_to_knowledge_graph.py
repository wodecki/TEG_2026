"""
Data to Knowledge Graph Conversion
==================================

Extracts data from PDFs and JSONs, converts them to a knowledge graph using
LangChain's LLMGraphTransformer, and stores in Neo4j.

This creates the static knowledge base for programmer staffing GraphRAG system.
"""

from dotenv import load_dotenv
load_dotenv(override=True)

import os
import asyncio
from glob import glob
from typing import List
import logging
from pathlib import Path
import toml

from unstructured.partition.pdf import partition_pdf
from langchain_core.documents import Document
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataKnowledgeGraphBuilder:
    """Builds knowledge graph from PDFs and JSONs using LangChain's LLMGraphTransformer."""

    def __init__(self, config_path: str = "utils/config.toml"):
        """Initialize the data knowledge graph builder."""
        self.config = self._load_config(config_path)
        self.setup_neo4j()
        self.setup_llm_transformer()

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from TOML file."""
        if not os.path.exists(config_path):
            raise ValueError(f"Configuration file not found: {config_path}")

        with open(config_path, 'r') as f:
            config = toml.load(f)

        return config

    def setup_neo4j(self):
        """Setup Neo4j connection."""
        try:
            self.graph = Neo4jGraph()
            logger.info("✓ Connected to Neo4j successfully")

            # Complete cleanup for fresh start
            logger.info("Performing complete Neo4j cleanup...")
            self.complete_cleanup()
            logger.info("✓ Neo4j completely cleared")

        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    def complete_cleanup(self):
        """Perform complete Neo4j database cleanup."""
        try:
            # Step 1: Delete all nodes and relationships
            logger.info("  - Deleting all nodes and relationships...")
            self.graph.query("MATCH (n) DETACH DELETE n")

            # Step 2: Drop all constraints
            logger.info("  - Dropping all constraints...")
            constraints_query = "SHOW CONSTRAINTS"
            constraints = self.graph.query(constraints_query)
            for constraint in constraints:
                constraint_name = constraint.get('name', '')
                if constraint_name:
                    try:
                        drop_query = f"DROP CONSTRAINT {constraint_name}"
                        self.graph.query(drop_query)
                        logger.debug(f"    Dropped constraint: {constraint_name}")
                    except Exception as e:
                        logger.debug(f"    Could not drop constraint {constraint_name}: {e}")

            # Step 3: Drop all indexes
            logger.info("  - Dropping all indexes...")
            indexes_query = "SHOW INDEXES"
            indexes = self.graph.query(indexes_query)
            for index in indexes:
                index_name = index.get('name', '')
                if index_name and not index_name.startswith('__'):  # Skip system indexes
                    try:
                        drop_query = f"DROP INDEX {index_name}"
                        self.graph.query(drop_query)
                        logger.debug(f"    Dropped index: {index_name}")
                    except Exception as e:
                        logger.debug(f"    Could not drop index {index_name}: {e}")

            # Step 4: Verify cleanup
            node_count = self.graph.query("MATCH (n) RETURN count(n) as count")[0]['count']
            rel_count = self.graph.query("MATCH ()-[r]->() RETURN count(r) as count")[0]['count']

            if node_count == 0 and rel_count == 0:
                logger.info("  ✓ Database completely clean")
            else:
                logger.warning(f"  ⚠ Cleanup incomplete: {node_count} nodes, {rel_count} relationships remain")

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            # Fallback to basic cleanup
            logger.info("  - Falling back to basic cleanup...")
            self.graph.query("MATCH (n) DETACH DELETE n")

    def setup_llm_transformer(self):
        """Setup LLM and graph transformer with CV-specific schema."""
        # Initialize LLM - using GPT-4o-mini for cost efficiency
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )

        # Define CV-specific ontology
        self.allowed_nodes = [
            "Person", "Company", "University", "Skill", "Technology",
            "Project", "Certification", "Location", "JobTitle", "Industry"
        ]

        # Define relationships with directional tuples
        self.allowed_relationships = [
            ("Person", "WORKED_AT", "Company"),
            ("Person", "STUDIED_AT", "University"),
            ("Person", "HAS_SKILL", "Skill"),
            ("Person", "LOCATED_IN", "Location"),
            ("Person", "HOLDS_POSITION", "JobTitle"),
            ("Person", "WORKED_ON", "Project"),
            ("Person", "EARNED", "Certification"),
            ("JobTitle", "AT_COMPANY", "Company"),
            ("Project", "USED_TECHNOLOGY", "Technology"),
            ("Project", "FOR_COMPANY", "Company"),
            ("Company", "IN_INDUSTRY", "Industry"),
            ("Skill", "RELATED_TO", "Technology"),
            ("Certification", "ISSUED_BY", "Company"),
            ("University", "LOCATED_IN", "Location")
        ]

        # Initialize transformer with strict schema
        self.llm_transformer = LLMGraphTransformer(
            llm=self.llm,
            allowed_nodes=self.allowed_nodes,
            allowed_relationships=self.allowed_relationships,
            node_properties=["start_date", "end_date", "level", "years_experience"],
            strict_mode=True
        )

        logger.info("✓ LLM Graph Transformer initialized with CV schema")

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from PDF using unstructured.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            str: Extracted text content
        """
        try:
            # Use unstructured to parse PDF
            elements = partition_pdf(filename=pdf_path)

            # Combine all text elements into single document
            # This is crucial - processing as single document maintains context
            full_text = "\n\n".join([str(element) for element in elements])

            logger.debug(f"Extracted {len(full_text)} characters from {pdf_path}")
            return full_text

        except Exception as e:
            logger.error(f"Failed to extract text from {pdf_path}: {e}")
            return ""

    async def convert_cv_to_graph(self, pdf_path: str) -> List:
        """Convert a single CV PDF to graph documents.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            List: Graph documents extracted from the CV
        """
        logger.info(f"Processing: {Path(pdf_path).name}")

        # Extract text from PDF
        text_content = self.extract_text_from_pdf(pdf_path)

        if not text_content.strip():
            logger.warning(f"No text extracted from {pdf_path}")
            return []

        # Create Document object
        document = Document(
            page_content=text_content,
            metadata={"source": pdf_path, "type": "cv"}
        )

        # Convert to graph documents using LLM
        try:
            graph_documents = await self.llm_transformer.aconvert_to_graph_documents([document])
            logger.info(f"✓ Extracted graph from {Path(pdf_path).name}")

            # Log extraction statistics
            if graph_documents:
                nodes_count = len(graph_documents[0].nodes)
                relationships_count = len(graph_documents[0].relationships)
                logger.info(f"  - Nodes: {nodes_count}, Relationships: {relationships_count}")

            return graph_documents

        except Exception as e:
            logger.error(f"Failed to convert {pdf_path} to graph: {e}")
            return []

    async def process_all_cvs(self, cv_directory: str = None) -> int:
        """Process all PDF CVs in the directory.

        Args:
            cv_directory: Directory containing PDF CVs (defaults to config value)

        Returns:
            int: Number of successfully processed CVs
        """
        # Use config directory if not specified
        if cv_directory is None:
            cv_directory = self.config['output']['programmers_dir']

        # Find all PDF files
        pdf_pattern = os.path.join(cv_directory, "*.pdf")
        pdf_files = glob(pdf_pattern)

        if not pdf_files:
            logger.error(f"No PDF files found in {cv_directory}")
            return 0

        logger.info(f"Found {len(pdf_files)} PDF files to process")

        processed_count = 0
        all_graph_documents = []

        # Process each CV
        for pdf_path in pdf_files:
            graph_documents = await self.convert_cv_to_graph(pdf_path)

            if graph_documents:
                all_graph_documents.extend(graph_documents)
                processed_count += 1
            else:
                logger.warning(f"Failed to process {pdf_path}")

        # Store all graph documents in Neo4j
        if all_graph_documents:
            logger.info("Storing graph documents in Neo4j...")
            self.store_graph_documents(all_graph_documents)

        return processed_count

    def store_graph_documents(self, graph_documents: List):
        """Store graph documents in Neo4j.

        Args:
            graph_documents: List of GraphDocument objects
        """
        try:
            # Add graph documents to Neo4j with enhanced options
            self.graph.add_graph_documents(
                graph_documents,
                baseEntityLabel=True,  # Add base Entity label for indexing
                include_source=True    # Include source documents for RAG
            )

            # Calculate and log statistics
            total_nodes = sum(len(doc.nodes) for doc in graph_documents)
            total_relationships = sum(len(doc.relationships) for doc in graph_documents)

            logger.info(f"✓ Stored {len(graph_documents)} documents in Neo4j")
            logger.info(f"✓ Total nodes: {total_nodes}")
            logger.info(f"✓ Total relationships: {total_relationships}")

            # Create useful indexes for performance
            self.create_indexes()

        except Exception as e:
            logger.error(f"Failed to store graph documents: {e}")
            raise

    def create_indexes(self):
        """Create indexes for better query performance."""
        indexes = [
            "CREATE INDEX person_name IF NOT EXISTS FOR (p:Person) ON (p.id)",
            "CREATE INDEX company_name IF NOT EXISTS FOR (c:Company) ON (c.id)",
            "CREATE INDEX skill_name IF NOT EXISTS FOR (s:Skill) ON (s.id)",
            "CREATE INDEX entity_base IF NOT EXISTS FOR (e:__Entity__) ON (e.id)"
        ]

        for index_query in indexes:
            try:
                self.graph.query(index_query)
                logger.debug(f"Created index: {index_query}")
            except Exception as e:
                logger.debug(f"Index might already exist: {e}")

    def validate_graph(self):
        """Validate the created knowledge graph."""
        logger.info("Validating knowledge graph...")

        # Basic statistics
        queries = {
            "Total nodes": "MATCH (n) RETURN count(n) as count",
            "Total relationships": "MATCH ()-[r]->() RETURN count(r) as count",
            "Node types": "MATCH (n) RETURN labels(n)[0] as type, count(n) as count ORDER BY count DESC",
            "Relationship types": "MATCH ()-[r]->() RETURN type(r) as type, count(r) as count ORDER BY count DESC"
        }

        for description, query in queries.items():
            try:
                result = self.graph.query(query)
                if description in ["Total nodes", "Total relationships"]:
                    logger.info(f"{description}: {result[0]['count']}")
                else:
                    logger.info(f"\n{description}:")
                    for row in result[:10]:  # Show top 10
                        if 'type' in row:
                            logger.info(f"  {row['type']}: {row['count']}")
                        else:
                            logger.info(f"  {row}")

            except Exception as e:
                logger.error(f"Failed to execute validation query '{description}': {e}")

        # Sample queries to verify extraction quality
        sample_queries = [
            "MATCH (p:Person)-[:HAS_SKILL]->(s:Skill) RETURN p.id, s.id LIMIT 5",
            "MATCH (p:Person)-[:WORKED_AT]->(c:Company) RETURN p.id, c.id LIMIT 5"
        ]

        logger.info("\nSample relationships:")
        for query in sample_queries:
            try:
                result = self.graph.query(query)
                for row in result:
                    logger.info(f"  {dict(row)}")
            except Exception as e:
                logger.debug(f"Sample query failed: {e}")


async def main():
    """Main function to convert CVs to knowledge graph."""
    print("Converting PDF CVs to Knowledge Graph")
    print("=" * 50)

    try:
        # Initialize builder
        builder = DataKnowledgeGraphBuilder()

        # Process all CVs
        processed_count = await builder.process_all_cvs()

        if processed_count > 0:
            # Validate the graph
            builder.validate_graph()

            print(f"\n✓ Successfully processed {processed_count} CV(s)")
            print("✓ Knowledge graph created in Neo4j")
            print("\nNext steps:")
            print("1. Run: uv run python 3_query_knowledge_graph.py")
            print("2. Open Neo4j Browser to explore the graph")
            print("3. Try GraphRAG queries!")
        else:
            print("❌ No CVs were successfully processed")
            print("Please check the PDF files in data/cvs_pdf/ directory")

    except Exception as e:
        logger.error(f"Failed to build knowledge graph: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())