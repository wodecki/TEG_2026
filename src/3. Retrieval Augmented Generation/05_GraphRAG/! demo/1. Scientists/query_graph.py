from dotenv import load_dotenv
load_dotenv(override=True)

from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

graph = Neo4jGraph(url="bolt://localhost:7687", username="neo4j", password="password")

cypher_prompt = PromptTemplate(
    input_variables=["schema", "question"],
    template="""Generate a Cypher query that answers the question, using only this graph schema:
{schema}

Matching rules:
- Match text properties partially and case-insensitively: WHERE toLower(x.id) CONTAINS toLower("keyword")
- Never match an id with exact equality (=).
- Pick the shortest distinctive keyword from the question (for example "Cambridge", "Nobel Prize").
- For multi-hop questions, connect every hop through shared node variables. If you use more
  than one MATCH clause, each clause must reuse a variable from a previous clause. Never leave
  two MATCH clauses joined only by RETURN.

Example multi-hop question: Which scientists won the same award as a scientist born in Germany?
MATCH (g:Scientist)-[:BORN_IN]->(c:Country)
WHERE toLower(c.id) CONTAINS toLower("germany")
MATCH (g)-[:WON]->(a:Award)<-[:WON]-(other:Scientist)
RETURN DISTINCT other.id

Return only the Cypher query.

Question: {question}""",
)

chain = GraphCypherQAChain.from_llm(
    llm=ChatOpenAI(model="gpt-5.4-mini", temperature=0),
    graph=graph,
    cypher_prompt=cypher_prompt,
    verbose=True,
    allow_dangerous_requests=True,
)

questions = [
    "Which scientists were born in England?",
    "How many scientists won a Nobel Prize?",
    "What did Marie Curie discover?",
    "Which scientists worked at Cambridge?",
    "Which scientists were born in the same country as Charles Darwin?",
    "Which scientist won the same award as Albert Einstein?",
    "Which scientists were born in the same country as a scientist who worked at Cambridge?",
    "How many discoveries were made by scientists born in England?",
]

for question in questions:
    answer = chain.invoke({"query": question})
    print(question)
    print(answer["result"])
    print()
