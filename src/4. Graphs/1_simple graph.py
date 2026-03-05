# Simple Graph Implementation with LangGraph
# Educational script demonstrating graph-based workflows and language model integration
#
# Required environment variables:
# - OPENAI_API_KEY: Your OpenAI API key for language model access

from dotenv import load_dotenv
import os
import random
import nest_asyncio
from typing import Literal, Annotated

# Third-party imports
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.graph.message import add_messages
from langgraph.prebuilt import tools_condition, ToolNode

# Load environment variables
load_dotenv(override=True)

# Apply nest_asyncio for Jupyter compatibility (if needed)
nest_asyncio.apply()

# ===== PART 1: GRAPHS AS SEQUENCES OF ACTIONS =====
# Graphs are sequences of actions, like steps in a process.
# These actions can be simple functions, language model modules, or entire subgraphs.

# ===== SIMPLE FUNCTIONS WITH STATES =====
# Each node is a function that modifies the graph state.
# State is represented by a dictionary storing variables and their values.

class State(TypedDict):
    graph_state: str

# ===== NODES =====
# Nodes are where functions change the state of the graph.
# Starting with elementary functions.

def node_1(state):
    print("--- Node 1 ---")
    return {"graph_state": state['graph_state'] + " I am"}

def node_2(state):
    print("--- Node 2 ---")
    return {"graph_state": state['graph_state'] + " happy :)"}

def node_3(state):
    print("--- Node 3 ---")
    return {"graph_state": state['graph_state'] + " sad :("}

# ===== EDGES =====
# Nodes are connected through edges that define task flow.
# They can be direct or conditional relationships.

def mood_decision(state) -> Literal["Node_2", "Node_3"]:
    """Conditional edge function that randomly decides the next node"""
    # Often the next step depends on the state
    # In this example, we use random choice but could analyze state['graph_state']

    # Let chance decide whether to choose node 2 or 3
    random_number = random.random()
    print(f"Random number: {random_number}")

    if random_number < 0.5:
        # 50% chance to choose node_2
        return "Node_2"

    # 50% chance to choose Node_3
    return "Node_3"

# ===== GRAPH CONSTRUCTION =====
# Design and create our simple graph

"""Create a simple graph with conditional routing"""
builder = StateGraph(State)
builder.add_node("Node_1", node_1)
builder.add_node("Node_2", node_2)
builder.add_node("Node_3", node_3)

builder.add_edge(START, "Node_1")
builder.add_conditional_edges("Node_1", mood_decision)
builder.add_edge("Node_2", END)
builder.add_edge("Node_3", END)

graph = builder.compile()

# ===== EXECUTION =====
"""Execute the simple graph with sample input"""

result = graph.invoke({"graph_state": "Hello, I am Tom."})
print(f"Final result: {result}")

# ===== PART 2: LANGUAGE MODEL AS A COMPONENT =====

# Initialize OpenAI language model
"""Initialize ChatOpenAI with API key from environment"""
api_key = os.getenv('OPENAI_API_KEY')
llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)

# Message state for handling conversation history
class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


def pure_llm(state: MessagesState):
    """Node that processes messages through the language model"""
    return {"messages": [llm.invoke(state["messages"])]}

# Build graph
builder = StateGraph(MessagesState)
builder.add_node("Pure_LLM", pure_llm)

builder.add_edge(START, "Pure_LLM")
builder.add_edge("Pure_LLM", END)

graph = builder.compile()

"""Execute the LLM graph with a sample question"""

result = graph.invoke({"messages": HumanMessage(content="Tell me about Paris")})

# Print the conversation
for message in result['messages']:
    if hasattr(message, 'content'):
        print(f"Message type: {type(message).__name__}")
        print(f"Content: {message.content[:200]}...")  # First 200 chars
        print("---")
