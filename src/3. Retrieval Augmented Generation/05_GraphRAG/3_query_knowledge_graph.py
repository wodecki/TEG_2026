"""
GraphRAG Query System for CV Knowledge Graph
============================================

Demonstrates GraphRAG capabilities by querying the knowledge graph
built from PDF CVs using natural language queries.

Shows advantages of structured graph queries over traditional RAG.
"""

from dotenv import load_dotenv
load_dotenv(override=True)

import os
from typing import List, Dict, Any
import logging

from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from langchain_openai import ChatOpenAI
from langchain_core.prompts.prompt import PromptTemplate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CVGraphRAGSystem:
    """GraphRAG system for querying CV-only knowledge graph.

    Enables natural language queries on knowledge graphs built from CV data,
    including Person nodes with skills, education, work experience, and certifications.
    """

    def __init__(self):
        """Initialize the GraphRAG system."""
        self.setup_neo4j()
        self.setup_qa_chain()
        self.load_example_queries()

    def setup_neo4j(self):
        """Setup Neo4j connection."""
        try:
            self.graph = Neo4jGraph(
                url="bolt://localhost:7687",
                username="neo4j",
                password="password123"
            )
            logger.info("✓ Connected to Neo4j successfully")

            # Refresh schema for accurate query generation
            self.graph.refresh_schema()
            logger.info("✓ Graph schema refreshed")

        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            print("❌ Could not connect to Neo4j. Make sure it's running:")
            print("   ./start_session.sh")
            raise

    def setup_qa_chain(self):
        """Setup the GraphCypherQA chain."""
        # Initialize LLM for query generation
        self.llm = ChatOpenAI(
            model="gpt-4o",  # Use more powerful model for query generation
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )

        # Custom Cypher generation prompt with case-insensitive matching
        CYPHER_GENERATION_TEMPLATE = """Task: Generate Cypher statement to query a graph database.
Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
For skill matching, always use case-insensitive comparison using toLower() function.
For count queries, ensure you return meaningful column names.

Schema:
{schema}

Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.

Examples: Here are a few examples of generated Cypher statements for particular questions:

# How many Python programmers do we have?
MATCH (p:Person)-[:HAS_SKILL]->(s:Skill)
WHERE toLower(s.id) = toLower("Python")
RETURN count(p) AS pythonProgrammers

# Who has React skills?
MATCH (p:Person)-[:HAS_SKILL]->(s:Skill)
WHERE toLower(s.id) = toLower("React")
RETURN p.id AS name

# Find people with both Python and Django skills
MATCH (p:Person)-[:HAS_SKILL]->(s1:Skill), (p)-[:HAS_SKILL]->(s2:Skill)
WHERE toLower(s1.id) = toLower("Python") AND toLower(s2.id) = toLower("Django")
RETURN p.id AS name

The question is:
{question}"""

        CYPHER_GENERATION_PROMPT = PromptTemplate(
            input_variables=["schema", "question"],
            template=CYPHER_GENERATION_TEMPLATE
        )

        # Custom QA prompt for better handling of numeric results
        CYPHER_QA_TEMPLATE = """You are an assistant that helps to form nice and human understandable answers.
The information part contains the result(s) of a Cypher query that was executed against a knowledge graph.
Information is provided as a list of records from the graph database.

Guidelines:
- If the information contains count results or numbers, state the exact count clearly.
- For count queries that return 0, say "There are 0 [items]" - this is a valid result, not missing information.
- If the information is empty or null, then say you don't know the answer.
- Use the provided information to construct a helpful answer.
- Be specific and mention actual names, numbers, or details from the information.

Information:
{context}

Question: {question}
Helpful Answer:"""

        CYPHER_QA_PROMPT = PromptTemplate(
            input_variables=["context", "question"],
            template=CYPHER_QA_TEMPLATE
        )

        # Create the GraphCypher QA chain with custom prompts
        self.qa_chain = GraphCypherQAChain.from_llm(
            llm=self.llm,
            graph=self.graph,
            verbose=True,  # Show generated Cypher queries
            cypher_prompt=CYPHER_GENERATION_PROMPT,
            qa_prompt=CYPHER_QA_PROMPT,
            return_intermediate_steps=True,
            allow_dangerous_requests=True  # Allow DELETE operations for demo
        )

        logger.info("✓ GraphCypher QA chain initialized with custom prompts")

    def load_example_queries(self):
        """Load example queries that demonstrate GraphRAG capabilities for CV data."""
        self.example_queries = {
            "Basic Information": [
                "How many people are in the knowledge graph?",
                "What companies appear in the CVs?",
                "List all the skills mentioned in the CVs.",
                "What certifications do people have?",
                "Which universities appear in the CVs?",
                "What job titles are mentioned?",
                "Show me all the locations where people are based."
            ],

            "Skill-based Queries": [
                "Who has Python programming skills?",
                "Find all people with React experience.",
                "Who has both Docker and Kubernetes skills?",
                "List people with JavaScript skills.",
                "Find people who know both Python and Django.",
                "Who has cloud computing skills like AWS?",
                "What programming languages are most common?",
                "Find people with machine learning expertise."
            ],

            "Company Experience": [
                "Who worked at Google?",
                "Find people who worked at Microsoft.",
                "What companies have the most former employees in our database?",
                "Who worked at technology companies?",
                "Find people with startup experience.",
                "List all companies mentioned in the CVs.",
                "Who has experience at Fortune 500 companies?"
            ],

            "Education Background": [
                "Who studied at Stanford University?",
                "Find people with computer science education.",
                "What universities are most common in our database?",
                "Who has a Master's degree?",
                "Find people who studied at Ivy League schools.",
                "What are the most common degree types?",
                "Who has a PhD?"
            ],

            "Location and Geography": [
                "Who is located in San Francisco?",
                "Find people in California.",
                "What cities have the most people?",
                "Who is located in New York?",
                "Find people in the United States.",
                "Show all locations in our database.",
                "Find people willing to relocate."
            ],

            "Professional Experience": [
                "Who has the most years of experience?",
                "Find senior-level professionals.",
                "Who worked in software development roles?",
                "Find people with leadership experience.",
                "Who has experience in data science?",
                "List all job titles mentioned.",
                "Find people with consulting experience."
            ],

            "Multi-hop Reasoning": [
                "Find people who worked at the same companies.",
                "Who went to the same university and has similar skills?",
                "Find people who have complementary skills for a team.",
                "What skills are commonly paired together?",
                "Find potential colleagues based on shared experience.",
                "Who studied at top universities and has industry experience?",
                "Find people with both technical and business skills."
            ],

            "Certification Analysis": [
                "Who has AWS certifications?",
                "Find all Google Cloud certified people.",
                "What are the most common certifications?",
                "Who has multiple certifications?",
                "Find people with security certifications.",
                "List all certification providers.",
                "Who has recent certifications?"
            ]
        }

    def query_graph(self, question: str) -> Dict[str, Any]:
        """Execute a natural language query against the graph.

        Args:
            question: Natural language question

        Returns:
            Dict containing query results and metadata
        """
        try:
            logger.info(f"Executing query: {question}")

            # Execute the query
            result = self.qa_chain.invoke({"query": question})

            # Extract components
            response = {
                "question": question,
                "answer": result.get("result", "No answer generated"),
                "cypher_query": result.get("intermediate_steps", [{}])[0].get("query", ""),
                "success": True
            }

            logger.info(f"✓ Query executed successfully")
            return response

        except Exception as e:
            logger.error(f"Query failed: {e}")
            return {
                "question": question,
                "answer": f"Error: {str(e)}",
                "cypher_query": "",
                "success": False
            }

    def run_example_queries(self, category: str = None) -> List[Dict[str, Any]]:
        """Run example queries to demonstrate GraphRAG capabilities.

        Args:
            category: Optional category to filter queries

        Returns:
            List of query results
        """
        results = []

        categories_to_run = [category] if category else self.example_queries.keys()

        for cat in categories_to_run:
            if cat not in self.example_queries:
                logger.warning(f"Category '{cat}' not found")
                continue

            print(f"\n{'='*60}")
            print(f"Category: {cat}")
            print(f"{'='*60}")

            for question in self.example_queries[cat]:
                print(f"\n🔍 Query: {question}")
                print("-" * 40)

                result = self.query_graph(question)
                results.append(result)

                if result["success"]:
                    print(f"📊 Generated Cypher: {result['cypher_query']}")
                    print(f"💡 Answer: {result['answer']}")
                else:
                    print(f"❌ Error: {result['answer']}")

                print()

        return results

    def custom_query(self, question: str) -> None:
        """Execute a custom user query.

        Args:
            question: User's natural language question
        """
        print(f"\n🔍 Custom Query: {question}")
        print("-" * 50)

        result = self.query_graph(question)

        if result["success"]:
            print(f"📊 Generated Cypher: {result['cypher_query']}")
            print(f"💡 Answer: {result['answer']}")
        else:
            print(f"❌ Error: {result['answer']}")

    def validate_graph_content(self) -> bool:
        """Validate that the graph has content for querying."""
        # First, get all available node labels
        try:
            labels_result = self.graph.query(
                "CALL db.labels() YIELD label RETURN label ORDER BY label"
            )
            available_labels = [row["label"] for row in labels_result if row["label"] != "__Entity__"]
        except:
            available_labels = []

        # Build validation queries based on available labels
        validation_queries = [
            ("Total nodes", "MATCH (n) RETURN count(n) as count"),
            ("Total relationships", "MATCH ()-[r]->() RETURN count(r) as count")
        ]

        # Add queries for available node types
        common_labels = ["Person", "Company", "Skill", "University", "Certification", "Project", "Location"]
        for label in common_labels:
            if label in available_labels:
                validation_queries.append((f"{label} count", f"MATCH (n:{label}) RETURN count(n) as count"))

        print("\n📊 Graph Validation")
        print("-" * 30)

        total_nodes = 0
        person_count = 0

        for description, query in validation_queries:
            try:
                result = self.graph.query(query)
                count = result[0]["count"] if result else 0
                print(f"{description}: {count:,}")

                if description == "Total nodes":
                    total_nodes = count
                elif description == "Person count":
                    person_count = count

            except Exception as e:
                print(f"{description}: Error - {e}")

        # Show relationship breakdown based on available relationships
        print("\n🔗 Key Relationships:")

        # Get all relationship types
        try:
            rel_result = self.graph.query(
                "CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType ORDER BY relationshipType"
            )
            available_rels = [row["relationshipType"] for row in rel_result]
        except:
            available_rels = []

        # Build relationship queries for common patterns
        common_rel_patterns = [
            ("Person-Skill connections", "MATCH (p:Person)-[r]->(s:Skill) RETURN count(*) as count"),
            ("Person-Company connections", "MATCH (p:Person)-[r]->(c:Company) RETURN count(*) as count"),
            ("Person-University connections", "MATCH (p:Person)-[r]->(u:University) RETURN count(*) as count"),
            ("Person-Location connections", "MATCH (p:Person)-[r]->(l:Location) RETURN count(*) as count"),
            ("Person-Certification connections", "MATCH (p:Person)-[r]->(cert:Certification) RETURN count(*) as count")
        ]

        for description, query in common_rel_patterns:
            try:
                result = self.graph.query(query)
                count = result[0]["count"] if result else 0
                if count > 0:  # Only show relationships that exist
                    print(f"{description}: {count:,}")
            except Exception as e:
                # Silently skip if node types don't exist
                pass

        # Show available labels and relationships
        if available_labels:
            print(f"\n🏷️  Available Node Types: {', '.join(available_labels)}")
        if available_rels:
            print(f"🔗 Available Relationships: {', '.join(available_rels)}")

        # Check if we have enough data
        if person_count == 0:
            print("\n⚠️  Warning: No Person nodes found in the graph!")
            print("Please run 2_data_to_knowledge_graph.py first to populate the graph.")
            print("Or check: uv run python 0_setup.py --check")
            return False

        if total_nodes < 10:
            print(f"\n⚠️  Warning: Only {total_nodes} nodes found. Consider generating more data.")

        print(f"\n✅ Graph validation successful: {person_count} people, {total_nodes} total nodes")
        return True

    def show_graph_schema(self) -> None:
        """Display the current graph schema."""
        print("\n📋 Graph Schema")
        print("-" * 30)

        try:
            # Get all node labels using CALL db.labels()
            try:
                labels_result = self.graph.query("CALL db.labels() YIELD label RETURN label ORDER BY label")
                node_labels = [row["label"] for row in labels_result if row["label"] != "__Entity__"]
            except:
                # Fallback method
                labels_result = self.graph.query(
                    "MATCH (n) RETURN DISTINCT labels(n) as labels ORDER BY labels[0]"
                )
                node_labels = []
                for label_row in labels_result:
                    labels = label_row["labels"]
                    if labels:
                        main_labels = [l for l in labels if l != "__Entity__"]
                        node_labels.extend(main_labels)
                node_labels = sorted(list(set(node_labels)))

            print("🏷️  Node Types:")
            if node_labels:
                for label in node_labels:
                    # Get count for each label
                    try:
                        count_result = self.graph.query(f"MATCH (n:{label}) RETURN count(n) as count")
                        count = count_result[0]["count"] if count_result else 0
                        print(f"   • {label} ({count:,} nodes)")
                    except:
                        print(f"   • {label}")
            else:
                print("   No node types found")

            # Get relationship types
            try:
                rel_result = self.graph.query("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType ORDER BY relationshipType")
                rel_types = [row["relationshipType"] for row in rel_result]
            except:
                # Fallback method
                rel_result = self.graph.query(
                    "MATCH ()-[r]->() RETURN DISTINCT type(r) as rel_type ORDER BY rel_type"
                )
                rel_types = [row["rel_type"] for row in rel_result]

            print("\n🔗 Relationship Types:")
            if rel_types:
                for rel_type in rel_types:
                    # Get count for each relationship type
                    try:
                        count_result = self.graph.query(f"MATCH ()-[r:{rel_type}]->() RETURN count(r) as count")
                        count = count_result[0]["count"] if count_result else 0
                        print(f"   • {rel_type} ({count:,} relationships)")
                    except:
                        print(f"   • {rel_type}")
            else:
                print("   No relationships found")

            # Show sample data
            print("\n📊 Sample Data:")

            # Sample people (try different property names)
            people_queries = [
                ("MATCH (p:Person) RETURN p.id as name LIMIT 3", "id"),
                ("MATCH (p:Person) RETURN p.name as name LIMIT 3", "name"),
                ("MATCH (p:Person) RETURN keys(p)[0] as prop, p[keys(p)[0]] as name LIMIT 3", "first_property")
            ]

            people_found = False
            for query, prop_type in people_queries:
                try:
                    people_sample = self.graph.query(query)
                    if people_sample and people_sample[0].get("name"):
                        print(f"   People (via {prop_type}):")
                        for person in people_sample[:3]:
                            if person.get("name"):
                                print(f"     - {person['name']}")
                        people_found = True
                        break
                except:
                    continue

            if not people_found:
                try:
                    # Show first 3 Person nodes with any available properties
                    people_sample = self.graph.query("MATCH (p:Person) RETURN p LIMIT 3")
                    if people_sample:
                        print("   People (raw properties):")
                        for person in people_sample:
                            node_props = person.get("p", {})
                            if isinstance(node_props, dict) and node_props:
                                # Show first property value
                                first_key = list(node_props.keys())[0]
                                print(f"     - {node_props[first_key]} ({first_key})")
                except:
                    pass

            # Sample skills
            skills_queries = [
                ("MATCH (s:Skill) RETURN s.id as skill LIMIT 5", "id"),
                ("MATCH (s:Skill) RETURN s.name as skill LIMIT 5", "name")
            ]

            for query, prop_type in skills_queries:
                try:
                    skills_sample = self.graph.query(query)
                    if skills_sample and skills_sample[0].get("skill"):
                        print(f"   Skills (via {prop_type}):")
                        for skill in skills_sample[:5]:
                            if skill.get("skill"):
                                print(f"     - {skill['skill']}")
                        break
                except:
                    continue

        except Exception as e:
            print(f"Error displaying schema: {e}")
            print("\nFallback schema:")
            try:
                print(self.graph.schema)
            except:
                print("Unable to retrieve schema")

    def interactive_mode(self) -> None:
        """Start interactive query mode."""
        print("\n🎯 Interactive GraphRAG Query Mode")
        print("Type your questions or 'quit' to exit")
        print("-" * 40)

        while True:
            try:
                question = input("\n❓ Your question: ").strip()

                if question.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break

                if not question:
                    continue

                self.custom_query(question)

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


def main():
    """Main function to demonstrate GraphRAG capabilities on CV-only knowledge graph."""
    print("CV Knowledge Graph - GraphRAG Query System")
    print("Natural Language Queries for CV Data")
    print("=" * 50)

    try:
        # Initialize system
        system = CVGraphRAGSystem()

        # Validate graph content
        if not system.validate_graph_content():
            return

        # Show schema
        system.show_graph_schema()

        # Menu system
        while True:
            print("\n🎯 GraphRAG Demo Options:")
            print("1. Basic Information queries")
            print("2. Skill-based queries")
            print("3. Company Experience queries")
            print("4. Education Background queries")
            print("5. Professional Experience queries")
            print("6. Multi-hop Reasoning queries")
            print("7. Certification Analysis queries")
            print("8. Run ALL example queries")
            print("9. Interactive query mode")
            print("0. Exit")

            choice = input("\nSelect option (0-9): ").strip()

            if choice == "1":
                system.run_example_queries("Basic Information")
            elif choice == "2":
                system.run_example_queries("Skill-based Queries")
            elif choice == "3":
                system.run_example_queries("Company Experience")
            elif choice == "4":
                system.run_example_queries("Education Background")
            elif choice == "5":
                system.run_example_queries("Professional Experience")
            elif choice == "6":
                system.run_example_queries("Multi-hop Reasoning")
            elif choice == "7":
                system.run_example_queries("Certification Analysis")
            elif choice == "8":
                system.run_example_queries()
            elif choice == "9":
                system.interactive_mode()
            elif choice == "0":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid option. Please select 0-9.")

    except Exception as e:
        logger.error(f"System error: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()