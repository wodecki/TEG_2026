"""
LangChain Tools Introduction
===========================

This script demonstrates LangChain's approach to tools and agents:
1. Creating tools with the @tool decorator
2. Understanding the difference between manual tool execution and agent-based execution
3. Introduction to LangChain agents and tool calling patterns
4. Comparing raw OpenAI function calling vs LangChain abstractions

Key learning points:
- @tool decorator simplifies tool creation with automatic schema generation
- LangChain agents handle the tool execution loop automatically
- Tools can have rich docstrings for better model understanding
- AgentExecutor manages the conversation and tool execution flow
"""

import json
import os
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain import hub
from langchain.agents import AgentExecutor, create_tool_calling_agent
from dotenv import load_dotenv

# ================================
# SETUP AND CONFIGURATION
# ================================

load_dotenv(override=True)
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ================================
# LANGCHAIN TOOL DEFINITIONS
# ================================

@tool
def get_current_weather(location: str, unit: str = "fahrenheit") -> str:
    """
    Get the current weather in a given location.

    Args:
        location: The city and state, e.g. San Francisco, CA.
        unit: The unit of temperature, can be 'celsius' or 'fahrenheit'. Defaults to 'fahrenheit'.
    """
    weather_info = {
        "location": location,
        "temperature": "72",
        "unit": unit,
        "forecast": ["sunny", "windy"],
    }
    return json.dumps(weather_info)

@tool
def multiply(a: int, b: int) -> int:
    """
    Multiply two numbers together.

    Args:
        a: First number to multiply
        b: Second number to multiply
    """
    print(f"Multiplying {a} × {b} = {a * b}")
    return a * b

@tool
def add(a: int, b: int) -> int:
    """
    Add two numbers together.

    Args:
        a: First number to add
        b: Second number to add
    """
    print(f"Adding {a} + {b} = {a + b}")
    return a + b

# ================================
# EXAMPLE 1: BASIC TOOL USAGE (MANUAL)
# ================================

print("=== EXAMPLE 1: Manual Tool Execution ===")

# Bind tools to model
model_with_tools = model.bind_tools([get_current_weather, multiply])

# Get model response with tool calls
response = model_with_tools.invoke("What's the weather in San Francisco?")

print("Model response:")
print(f"Content: {response.content}")
print(f"Tool calls: {response.tool_calls}")
# Expected: Model returns tool call information, not executed results

if response.tool_calls:
    tool_call = response.tool_calls[0]
    print(f"\nTool to call: {tool_call['name']}")
    print(f"Arguments: {tool_call['args']}")

    # Manual execution using LangChain tool invoke method
    if tool_call['name'] == 'get_current_weather':
        result = get_current_weather.invoke(tool_call['args'])
        print(f"Manual execution result: {result}")

# ================================
# EXAMPLE 2: MODEL WITHOUT TOOLS
# ================================

print("\n=== EXAMPLE 2: Model Without Tools ===")

response = model.invoke("What's the weather in San Francisco?")
print("Response without tools:")
print(response.content)
# Expected: Model explains it cannot access weather data

# ================================
# EXAMPLE 3: LANGCHAIN AGENT (AUTOMATED)
# ================================

print("\n=== EXAMPLE 3: LangChain Agent with Tools ===")

# Get a pre-built prompt for tool-calling agents
prompt = hub.pull("hwchase17/openai-tools-agent")

# Create tools list
tools = [get_current_weather, multiply, add]

# Create agent
agent = create_tool_calling_agent(model, tools, prompt)

# Create executor (handles the tool execution loop)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

print("Query: What's 5 multiplied by 8?")
result = agent_executor.invoke({"input": "What's 5 multiplied by 8?"})
print(f"Agent result: {result['output']}")

# ================================
# EXAMPLE 4: COMPLEX MULTI-STEP QUERY
# ================================

print("\n=== EXAMPLE 4: Multi-Step Query ===")

complex_query = "Get the weather in Boston, then multiply the temperature by 2"
print(f"Complex query: {complex_query}")

result = agent_executor.invoke({"input": complex_query})
print(f"Multi-step result: {result['output']}")
# Expected: Agent calls weather function, extracts temperature, then calls multiply

# ================================
# EXAMPLE 5: TOOL INTROSPECTION
# ================================

print("\n=== EXAMPLE 5: Tool Introspection ===")

print("Available tools:")
for tool in tools:
    print(f"- {tool.name}: {tool.description}")
    print(f"  Schema: {tool.args_schema.model_json_schema()}")

# ================================
# EXAMPLE 6: COMPARING APPROACHES
# ================================

print("\n=== EXAMPLE 6: Comparing Approaches ===")

print("OpenAI Function Calling:")
print("+ Direct control over function execution")
print("+ Minimal abstraction")
print("- Manual conversation management")
print("- More boilerplate code")

print("\nLangChain Tools & Agents:")
print("+ Automatic tool execution loop")
print("+ Rich tool ecosystem")
print("+ Conversation management handled")
print("+ Easy tool composition")
print("- Additional abstraction layer")

print("\n=== Key Takeaways ===")
print("1. @tool decorator automatically generates schemas from docstrings")
print("2. LangChain agents handle the tool execution loop automatically")
print("3. AgentExecutor manages conversation flow and tool invocation")
print("4. Tools can be composed and reused across different agents")
print("5. Rich docstrings improve model understanding of tool purposes")