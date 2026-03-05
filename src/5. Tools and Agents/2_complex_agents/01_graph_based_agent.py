"""
Graph-Based Agent Implementation with LangGraph
==============================================

This script demonstrates the progression from basic LLMs to sophisticated
graph-based agents that can use tools effectively.

Learning Progression:
1. Basic LLM without tools
2. Tool-aware LLM (generates tool calls but doesn't execute them)
3. Tool executor graph (full ReAct pattern implementation)

Key concepts:
- LangGraph StateGraph construction
- Tool binding and execution
- Conditional routing based on tool calls
- Message state management
- Graph visualization and debugging
"""

from dotenv import load_dotenv
from typing import Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import tools_condition, ToolNode

# Load environment variables
load_dotenv(override=True)

# ================================
# UTILITY FUNCTIONS
# ================================

def initialize_llm():
    """Initialize the language model with consistent settings"""
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        streaming=False
    )

# ================================
# TOOL DEFINITIONS
# ================================

def multiply(a: int, b: int) -> int:
    """
    Multiply two numbers together.

    Args:
        a: First number to multiply
        b: Second number to multiply

    Returns:
        int: The product of a and b
    """
    print(f"🔢 Executing multiply: {a} × {b}")
    return a * b

def add(a: int, b: int) -> int:
    """
    Add two numbers together.

    Args:
        a: First number to add
        b: Second number to add

    Returns:
        int: The sum of a and b
    """
    print(f"➕ Executing add: {a} + {b}")
    return a + b

def divide(a: int, b: int) -> float:
    """
    Divide the first number by the second number.

    Args:
        a: Dividend (number to be divided)
        b: Divisor (number to divide by)

    Returns:
        float: The result of a divided by b
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")

    print(f"➗ Executing divide: {a} ÷ {b}")
    return a / b

# ================================
# EXAMPLE 1: BASIC LLM (NO TOOLS)
# ================================

def create_basic_llm_graph():
    """Create a simple graph with just an LLM node"""
    llm = initialize_llm()

    def llm_node(state: MessagesState):
        """Simple LLM node that processes messages"""
        return {"messages": [llm.invoke(state["messages"])]}

    # Build the graph
    builder = StateGraph(MessagesState)
    builder.add_node("llm", llm_node)
    builder.add_edge(START, "llm")
    builder.add_edge("llm", END)

    return builder.compile()

# ================================
# EXAMPLE 2: TOOL-AWARE LLM (NO EXECUTION)
# ================================

def create_tool_aware_graph():
    """
    Create a graph with LLM that can generate tool calls but doesn't execute them.
    This shows how models decide when to use tools.
    """
    llm = initialize_llm()
    tools = [add, multiply, divide]
    tool_aware_llm = llm.bind_tools(tools)

    def llm_with_tools(state: MessagesState):
        """Node that generates tool calls but doesn't execute them"""
        print("🧠 LLM analyzing query and deciding on tool usage...")
        response = tool_aware_llm.invoke(state["messages"])

        if hasattr(response, 'tool_calls') and response.tool_calls:
            print(f"🔧 Model wants to use {len(response.tool_calls)} tool(s)")
            for tool_call in response.tool_calls:
                print(f"   - {tool_call['name']} with args: {tool_call['args']}")
        else:
            print("💬 Model chose to respond directly without tools")

        return {"messages": [response]}

    # Build graph
    builder = StateGraph(MessagesState)
    builder.add_node("llm_with_tools", llm_with_tools)
    builder.add_edge(START, "llm_with_tools")
    builder.add_edge("llm_with_tools", END)

    return builder.compile()

# ================================
# EXAMPLE 3: FULL TOOL EXECUTOR GRAPH
# ================================

def create_tool_executor_graph():
    """
    Create a complete ReAct agent that can both generate and execute tool calls.
    This demonstrates the full observe → think → act → observe cycle.
    """
    llm = initialize_llm()
    tools = [add, multiply, divide]
    tool_aware_llm = llm.bind_tools(tools)

    # System message for the assistant
    sys_msg = SystemMessage(content="""You are a helpful mathematical assistant.
    When performing calculations:
    1. Break down complex problems into steps
    2. Use the available tools for arithmetic operations
    3. Show your reasoning clearly
    4. Provide the final answer

    Available tools: add, multiply, divide""")

    def llm_with_tools(state: MessagesState):
        """Node that processes messages with full tool awareness"""
        print("🧠 Agent analyzing query and planning actions...")

        # Add system message to the conversation
        messages_with_system = [sys_msg] + state["messages"]
        response = tool_aware_llm.invoke(messages_with_system)

        if hasattr(response, 'tool_calls') and response.tool_calls:
            print(f"🔧 Agent decided to use {len(response.tool_calls)} tool(s)")
        else:
            print("💬 Agent providing final response")

        return {"messages": [response]}

    # Build graph with tool execution capability
    builder = StateGraph(MessagesState)
    builder.add_node("llm_with_tools", llm_with_tools)
    builder.add_node("tools", ToolNode(tools))

    # Define the flow
    builder.add_edge(START, "llm_with_tools")

    # Conditional routing based on whether the LLM made tool calls
    builder.add_conditional_edges(
        "llm_with_tools",
        tools_condition,  # If tool calls present → go to tools, else → END
    )

    # After tool execution, return to the LLM for processing results
    builder.add_edge("tools", "llm_with_tools")

    return builder.compile()

# ================================
# DEMONSTRATION AND TESTING
# ================================

def run_basic_llm_example():
    """Demonstrate basic LLM without tools"""
    print("=" * 50)
    print("EXAMPLE 1: Basic LLM (No Tools)")
    print("=" * 50)

    graph = create_basic_llm_graph()

    question = "What is 15 multiplied by 8?"
    print(f"Question: {question}")

    result = graph.invoke({"messages": [HumanMessage(content=question)]})
    print(f"Response: {result['messages'][-1].content}")
    print("Note: Without tools, the LLM can only provide estimates or explanations\n")

def run_tool_aware_example():
    """Demonstrate tool-aware LLM that generates but doesn't execute tool calls"""
    print("=" * 50)
    print("EXAMPLE 2: Tool-Aware LLM (No Execution)")
    print("=" * 50)

    graph = create_tool_aware_graph()

    questions = [
        "What is 15 multiplied by 8?",
        "Hello, how are you today?",
        "Calculate (25 + 10) divided by 5"
    ]

    for question in questions:
        print(f"\nQuestion: {question}")
        result = graph.invoke({"messages": [HumanMessage(content=question)]})

        final_message = result['messages'][-1]
        if hasattr(final_message, 'tool_calls') and final_message.tool_calls:
            print("Result: Tool calls generated but not executed")
            print("This shows the model's decision-making process")
        else:
            print(f"Result: {final_message.content}")
        print("-" * 30)

def run_tool_executor_example():
    """Demonstrate full tool executor graph with ReAct pattern"""
    print("=" * 50)
    print("EXAMPLE 3: Full Tool Executor (Complete ReAct)")
    print("=" * 50)

    graph = create_tool_executor_graph()

    questions = [
        "What is 15 multiplied by 8?",
        "Calculate (25 + 10) divided by 5",
        "I need to know: 144 divided by 12, then multiply that result by 7"
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n--- Test {i} ---")
        print(f"Question: {question}")

        result = graph.invoke({"messages": [HumanMessage(content=question)]})

        print(f"Final Answer: {result['messages'][-1].content}")
        print(f"Total messages in conversation: {len(result['messages'])}")
        print("-" * 40)

def analyze_graph_behavior():
    """Analyze and compare the different graph implementations"""
    print("=" * 50)
    print("GRAPH BEHAVIOR ANALYSIS")
    print("=" * 50)

    print("🔍 Key Differences Between Approaches:")
    print("1. Basic LLM: Direct text generation, no external capabilities")
    print("2. Tool-Aware: Generates structured tool calls, shows model reasoning")
    print("3. Tool Executor: Complete automation with actual tool execution")

    print("\n📊 Use Cases:")
    print("• Basic LLM: General conversation, explanation tasks")
    print("• Tool-Aware: Debugging agent decisions, understanding model behavior")
    print("• Tool Executor: Production agents, automated task completion")

    print("\n🧠 ReAct Pattern Components:")
    print("• Reason: LLM analyzes the problem")
    print("• Act: LLM decides which tools to use")
    print("• Observe: System executes tools and returns results")
    print("• Repeat: Continue until task is complete")

if __name__ == "__main__":
    print("Graph-Based Agent Demonstration")
    print("==============================")

    # Run all examples in sequence
    run_basic_llm_example()
    run_tool_aware_example()
    run_tool_executor_example()
    analyze_graph_behavior()

    print("\n✅ All examples completed!")
    print("💡 Key Takeaway: LangGraph enables building sophisticated agents")
    print("   with precise control over tool usage and conversation flow.")