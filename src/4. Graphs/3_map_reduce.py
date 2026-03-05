"""
Map-reduce pattern with LangGraph for generating and selecting jokes

Demonstrates:
- Map phase: Parallel joke generation on different subtopics
- Reduce phase: Selection of the best joke from generated set
"""

from dotenv import load_dotenv
import os

load_dotenv(override=True)

# Required environment variables:
# OPENAI_API_KEY - Your OpenAI API key

from langchain_openai import ChatOpenAI
import operator
from typing import Annotated
from typing_extensions import TypedDict
from pydantic import BaseModel
from langgraph.types import Send
from langgraph.graph import END, StateGraph, START
from langchain_core.runnables.graph import MermaidDrawMethod

# Check if API key is available
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Prompts used in the system
subjects_prompt = """Generate a list of several, max 5, subtopics that are related to the general topic: {topic}."""
joke_prompt = """Create a joke about {subject}"""
best_joke_prompt = """Below you will find several jokes about {topic}. Choose the best one! Return the ID of the best one, starting from 0 as the ID of the first joke. Jokes: \n\n  {jokes}"""

# LLM model with increased temperature for greater creativity
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# Pydantic models for structured responses
class Subjects(BaseModel):
    subjects: list[str]

class BestJoke(BaseModel):
    id: int

class Joke(BaseModel):
    joke: str

# Main graph state - 'jokes' key uses operator.add to aggregate results from parallel nodes
class OverallState(TypedDict):
    topic: str
    subjects: list
    jokes: Annotated[list, operator.add]
    best_selected_joke: str

# State for single joke generation node
class JokeState(TypedDict):
    subject: str

def generate_topics(state: OverallState):
    """Generates a list of subtopics based on the main topic"""
    prompt = subjects_prompt.format(topic=state["topic"])
    response = llm.with_structured_output(Subjects).invoke(prompt)
    return {"subjects": response.subjects}

def continue_to_jokes(state: OverallState):
    """
    Uses Send() for parallel joke generation for each subtopic.
    Send allows passing any state to the target node.
    """
    return [Send("generate_joke", {"subject": s}) for s in state["subjects"]]

def generate_joke(state: JokeState):
    """
    MAP PHASE: Generates a single joke on the given topic.
    Results are automatically aggregated in OverallState by operator.add.
    """
    prompt = joke_prompt.format(subject=state["subject"])
    response = llm.with_structured_output(Joke).invoke(prompt)
    return {"jokes": [response.joke]}

def best_joke(state: OverallState):
    """
    REDUCE PHASE: Selects the best joke from all generated ones.
    Aggregates results from MAP phase and makes final selection.
    """
    jokes = "\n\n".join(state["jokes"])
    prompt = best_joke_prompt.format(topic=state["topic"], jokes=jokes)
    response = llm.with_structured_output(BestJoke).invoke(prompt)
    return {"best_selected_joke": state["jokes"][response.id]}

# Map-reduce graph construction
graph = StateGraph(OverallState)
graph.add_node("generate_topics", generate_topics)
graph.add_node("generate_joke", generate_joke)
graph.add_node("best_joke", best_joke)

# Flow definition
graph.add_edge(START, "generate_topics")
graph.add_conditional_edges("generate_topics", continue_to_jokes, ["generate_joke"])
graph.add_edge("generate_joke", "best_joke")
graph.add_edge("best_joke", END)

# Graph compilation
app = graph.compile()

# Example usage - generating jokes about the future of banking
print("=== Running map-reduce process for joke generation ===")
print("Topic: future of banking")
print()

for s in app.stream({"topic": "future of banking"}):
    print(s)

print("\n=== Process completed ===")