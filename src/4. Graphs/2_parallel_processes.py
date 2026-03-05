"""
Parallel Node Execution in LangGraph

This script demonstrates parallel processing in LangGraph with two examples:
1. Simple asynchronous process with nodes adding names to a list
2. Parallel processing using LLM, Tavily and Wikipedia

In production environments, asynchronous processing and parallelization become
critical. This affects not only reducing user wait time for responses, but also
the ability to scale the system and containerize it.

Required environment variables:
- OPENAI_API_KEY: API key for OpenAI
- TAVILY_API_KEY: API key for Tavily (web search engine)
"""

from dotenv import load_dotenv
import os

load_dotenv(override=True)

import operator
from typing import Annotated, TypedDict, Any
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables.graph import MermaidDrawMethod
from langchain_community.document_loaders import WikipediaLoader
from langchain_community.tools.tavily_search import TavilySearchResults

# API key verification
openai_key = os.getenv('OPENAI_API_KEY')
tavily_key = os.getenv('TAVILY_API_KEY')

if not openai_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")
if not tavily_key:
    raise ValueError("TAVILY_API_KEY not found in environment variables")

# LLM model initialization
llm = ChatOpenAI(model="gpt-5-mini")

print("=== PART 1: SIMPLE ASYNCHRONOUS PROCESS ===")
print("Nodes introduce themselves and add their name to a single list")
print()

# State definition for simple example
class SimpleState(TypedDict):
    state: Annotated[list, operator.add]

class ReturnNodeValue:
    """Class representing a node that adds its value to the state"""

    def __init__(self, node_secret: str):
        self._value = node_secret

    def __call__(self, state: SimpleState) -> Any:
        print(f"Adding {self._value} to {state['state']}")
        return {"state": [self._value]}

# Creating graph for simple example
simple_builder = StateGraph(SimpleState)

# Adding nodes with unique names
simple_builder.add_node("a", ReturnNodeValue("I am A"))
simple_builder.add_node("b", ReturnNodeValue("I am B"))
simple_builder.add_node("c", ReturnNodeValue("I am C"))
simple_builder.add_node("d", ReturnNodeValue("I am D"))

# Flow definition - nodes b and c run in parallel after a
simple_builder.add_edge(START, "a")
simple_builder.add_edge("a", "b")  # parallel execution
simple_builder.add_edge("a", "c")  # parallel execution
simple_builder.add_edge("b", "d")
simple_builder.add_edge("c", "d")
simple_builder.add_edge("d", END)

simple_graph = simple_builder.compile()

# Running simple example
print("Running simple asynchronous graph:")
simple_result = simple_graph.invoke({"state": []})
print(f"Result: {simple_result}")
print()

print("=== PART 2: PARALLEL PROCESSING WITH LLM ===")
print("System answers questions using two sources: Internet (Tavily) and Wikipedia")
print()

# State definition for search example
class SearchState(TypedDict):
    question: str
    answer: str
    context: Annotated[list, operator.add]

def search_web(state):
    """Search internet resources using Tavily"""

    print("... Searching internet resources using Tavily ... \n")

    # Internet search
    tavily_search = TavilySearchResults(max_results=3)
    search_docs = tavily_search.invoke(state['question'])

    # Format results
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document href="{doc["url"]}"/>\n{doc["content"]}\n</Document>'
            for doc in search_docs
        ]
    )

    return {"context": [formatted_search_docs]}

def search_wikipedia(state):
    """Search Wikipedia resources"""

    print("... Searching Wikipedia resources ... \n")

    # Wikipedia search
    search_docs = WikipediaLoader(
        query=state['question'],
        load_max_docs=2
    ).load()

    # Format results
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}"/>\n{doc.page_content}\n</Document>'
            for doc in search_docs
        ]
    )

    return {"context": [formatted_search_docs]}

def generate_answer(state):
    """Generate answer based on collected context"""

    # Get state
    context = state["context"]
    question = state["question"]

    # Answer template
    answer_template = """Answer the question {question} using this context: {context}"""
    answer_instructions = answer_template.format(
        question=question,
        context=context
    )

    # Generate answer
    answer = llm.invoke([
        SystemMessage(content=answer_instructions),
        HumanMessage(content="Answer the question.")
    ])

    return {"answer": answer}

# Creating search graph
search_builder = StateGraph(SearchState)

# Adding nodes
search_builder.add_node("search_internet", search_web)
search_builder.add_node("search_wikipedia", search_wikipedia)
search_builder.add_node("generate_answer", generate_answer)

# Flow definition - searches run in parallel
search_builder.add_edge(START, "search_wikipedia")    # parallel execution
search_builder.add_edge(START, "search_internet")     # parallel execution
search_builder.add_edge("search_wikipedia", "generate_answer")
search_builder.add_edge("search_internet", "generate_answer")
search_builder.add_edge("generate_answer", END)

search_graph = search_builder.compile()

# Example question to demonstrate the system
example_question = "What is a business potential of LLM-based multi-agent systems in banking? Suggest the most interesting business cases"

print(f"Asking question: {example_question}")
print()

# Run search and answer generation
search_result = search_graph.invoke({"question": example_question})

print("=== ANSWER ===")
print(search_result['answer'].content)
print()

print("=== CONTEXT INFORMATION ===")
print(f"Collected {len(search_result['context'])} information sources:")
for i, context in enumerate(search_result['context'], 1):
    print(f"Source {i}: {len(context)} characters")

# Examples of other questions to try:
print("\n=== OTHER QUESTIONS TO TRY ===")
print("You can test the system with other questions, for example:")
print('- "What is the potential of generative technologies in banking?"')
print('- "What is the current state of floods in Poland?"')
print('- "What are the latest developments in artificial intelligence?"')
print()
print("To ask a new question, use:")
print('new_result = search_graph.invoke({"question": "your question"})')
print('print(new_result["answer"].content)')