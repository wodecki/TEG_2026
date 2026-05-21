from dotenv import load_dotenv
load_dotenv(override=True)

from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph
from langchain_core.documents import Document
from pathlib import Path

bios_dir = Path(__file__).parent / "scientists_bios"
bios = [Document(page_content=f.read_text()) for f in sorted(bios_dir.glob("*.txt"))]

transformer = LLMGraphTransformer(
    llm=ChatOpenAI(model="gpt-5.4-mini", temperature=0),
    allowed_nodes=["Scientist", "Field", "Country", "Institution", "Discovery", "Award"],
    allowed_relationships=[
        ("Scientist", "WORKED_IN", "Field"),
        ("Scientist", "BORN_IN", "Country"),
        ("Scientist", "WORKED_AT", "Institution"),
        ("Scientist", "DISCOVERED", "Discovery"),
        ("Scientist", "WON", "Award"),
        ("Scientist", "INFLUENCED", "Scientist"),
        ("Scientist", "COLLABORATED_WITH", "Scientist"),
    ],
)

graph_documents = transformer.convert_to_graph_documents(bios)

graph = Neo4jGraph(url="bolt://localhost:7687", username="neo4j", password="password")
graph.query("MATCH (n) DETACH DELETE n")
graph.add_graph_documents(graph_documents)

print(f"Created {sum(len(d.nodes) for d in graph_documents)} nodes and {sum(len(d.relationships) for d in graph_documents)} relationships in Neo4j")
