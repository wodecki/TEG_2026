"""
LangGraph ReAct Agent Foundation
===============================

This script demonstrates LangGraph's ReAct (Reasoning + Acting) agent pattern:
1. Creating agents with create_react_agent
2. Understanding stateful conversations with thread-based persistence
3. Multi-tool agents that can reason about tool selection
4. How LangGraph manages agent decision-making loops

Key learning points:
- ReAct agents combine reasoning and tool execution
- Stateful conversations persist across multiple interactions
- Agent graphs can be invoked with different configurations
- LangGraph handles the reasoning → action → observation cycle automatically
"""

import os
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from dotenv import load_dotenv

# ================================
# SETUP AND CONFIGURATION
# ================================

load_dotenv(override=True)

# Initialize the language model
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ================================
# TOOL DEFINITIONS
# ================================

@tool
def multiply(a: int, b: int) -> int:
    """
    Multiply two numbers together.

    Args:
        a: First number
        b: Second number
    """
    print(f"🔢 Computing: {a} × {b}")
    return a * b

@tool
def add(a: int, b: int) -> int:
    """
    Add two numbers together.

    Args:
        a: First number
        b: Second number
    """
    print(f"➕ Computing: {a} + {b}")
    return a + b

@tool
def power(a: int, b: int) -> int:
    """
    Calculate a raised to the power of b.

    Args:
        a: Base number
        b: Exponent
    """
    print(f"⚡ Computing: {a}^{b}")
    return a ** b

@tool
def get_word_length(word: str) -> int:
    """
    Get the length of a word in characters.

    Args:
        word: The word to measure
    """
    print(f"📏 Measuring word: '{word}'")
    return len(word)

# ================================
# AGENT CREATION
# ================================

# Define available tools
tools = [multiply, add, power, get_word_length]

# Create system prompt for the agent
system_prompt = """You are a helpful assistant that can perform calculations and text analysis.

When working with numbers, show your reasoning step by step.
When asked to perform multiple operations, break them down clearly.
Always explain what you're doing before using tools."""

# Create the ReAct agent
from langgraph.checkpoint.memory import MemorySaver

agent_graph = create_react_agent(
    llm,
    tools=tools,
    prompt=system_prompt,
    checkpointer=MemorySaver()
)

# ================================
# EXAMPLE 1: SIMPLE CALCULATION
# ================================

print("=== EXAMPLE 1: Simple Calculation ===")

session_id = "math_session_1"
config = {'configurable': {'thread_id': session_id}}

query1 = "What's 8 multiplied by 7?"
print(f"Query: {query1}")

response1 = agent_graph.invoke({'messages': [('user', query1)]}, config)
print(f"Response: {response1['messages'][-1].content}")
# Expected: Agent uses multiply tool and provides answer

# ================================
# EXAMPLE 2: MULTI-STEP CALCULATION
# ================================

print("\n=== EXAMPLE 2: Multi-Step Calculation ===")

query2 = "Calculate 5 to the power of 3, then add 20 to the result"
print(f"Query: {query2}")

response2 = agent_graph.invoke({'messages': [('user', query2)]}, config)
print(f"Response: {response2['messages'][-1].content}")
# Expected: Agent uses power tool, then add tool, shows reasoning

# ================================
# EXAMPLE 3: MIXED OPERATIONS
# ================================

print("\n=== EXAMPLE 3: Mixed Operations ===")

query3 = "How many characters are in the word 'LangGraph'? Then multiply that by 4."
print(f"Query: {query3}")

response3 = agent_graph.invoke({'messages': [('user', query3)]}, config)
print(f"Response: {response3['messages'][-1].content}")
# Expected: Agent uses get_word_length, then multiply tool

# ================================
# EXAMPLE 4: CONVERSATIONAL CONTEXT
# ================================

print("\n=== EXAMPLE 4: Conversational Context ===")

query4 = "Can you remind me what the result was from the previous calculation?"
print(f"Query: {query4}")

response4 = agent_graph.invoke({'messages': [('user', query4)]}, config)
print(f"Response: {response4['messages'][-1].content}")
# Expected: Agent remembers previous context due to thread persistence

# ================================
# EXAMPLE 5: NEW SESSION (NO CONTEXT)
# ================================

print("\n=== EXAMPLE 5: New Session (Fresh Context) ===")

new_session_id = "math_session_2"
new_config = {'configurable': {'thread_id': new_session_id}}

query5 = "What was the result from the previous calculation?"
print(f"Query: {query5}")

response5 = agent_graph.invoke({'messages': [('user', query5)]}, config)
print(f"Response: {response5['messages'][-1].content}")
# Expected: Agent has no memory of previous session

# ================================
# EXAMPLE 6: COMPLEX REASONING
# ================================

print("\n=== EXAMPLE 6: Complex Multi-Tool Reasoning ===")

complex_query = """
I have a word 'Python' and I want to:
1. Find out how many characters it has
2. Raise that number to the power of 2
3. Add 15 to the final result

Please work through this step by step.
"""

print(f"Complex Query: {complex_query.strip()}")

response6 = agent_graph.invoke({'messages': [('user', complex_query)]}, new_config)
print(f"Response: {response6['messages'][-1].content}")
# Expected: Agent uses all three tools in sequence with clear reasoning

# ================================
# EXAMPLE 7: AGENT DECISION MAKING
# ================================

print("\n=== EXAMPLE 7: Agent Decision Making ===")

query7 = "I need to do some math but I'm not sure what. Can you suggest something?"
print(f"Query: {query7}")

response7 = agent_graph.invoke({'messages': [('user', query7)]}, new_config)
print(f"Response: {response7['messages'][-1].content}")
# Expected: Agent provides suggestions without using tools

# ================================
# ANALYZING THE CONVERSATION
# ================================

print("\n=== CONVERSATION ANALYSIS ===")

print("Session 1 conversation history:")
session1_messages = agent_graph.get_state(config)
print(f"Total messages in session 1: {len(session1_messages.values['messages'])}")

print("\nSession 2 conversation history:")
session2_messages = agent_graph.get_state(new_config)
print(f"Total messages in session 2: {len(session2_messages.values['messages'])}")

print("\n=== Key Takeaways ===")
print("1. ReAct agents combine reasoning with tool execution automatically")
print("2. Thread-based persistence maintains conversation context")
print("3. Agents make intelligent decisions about which tools to use")
print("4. Multi-step reasoning is handled seamlessly")
print("5. Different thread IDs create separate conversation contexts")
print("6. LangGraph manages the observe → think → act cycle")