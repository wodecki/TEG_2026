import os
import tomllib  # For Python 3.11+, use tomli for earlier versions

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

from langchain_core.tools import tool

from langgraph_supervisor import create_supervisor

from typing import Annotated, Literal, TypedDict
from langgraph.graph.message import add_messages

from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    ToolMessage,
    AIMessage
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def create_agent(llm, tools, system_message: str):
    """Create an agent."""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "{system_message}",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    prompt = prompt.partial(system_message=system_message)
    if tools:
      return prompt | llm.bind_tools(tools)
    else:
      return prompt | llm


# Load environment variables
from dotenv import load_dotenv
load_dotenv(override=True)

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")

tavily = TavilySearchResults(max_results=5)
wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
arxiv = load_tools(["arxiv"])[0]

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)

# Load prompt templates from TOML file
with open("config/prompts.toml", "rb") as f:
    prompts = tomllib.load(f)

search_template = prompts["search"]["template"]
outliner_template = prompts["outliner"]["template"]
writer_template = prompts["writer"]["template"]
editor_template = prompts["editor"]["template"]

tools = [tavily, wikipedia, arxiv]

search_agent = create_agent(
    llm,
    tools,
    system_message=search_template,
)

outliner_agent = create_agent(
    llm,
    [],
    system_message=outliner_template,
)

writer_agent = create_agent(
    llm,
    [],
    system_message=writer_template,
)

editor_agent = create_agent(
    llm,
    [],
    system_message=editor_template,
)

# Helper function to create a node for a given agent
def agent_node(state, agent, name):
    result = agent.invoke(state)
    return {
        "messages": [result]
    }
    
import functools

search_node = functools.partial(agent_node, agent=search_agent, name="Search Agent")
outliner_node = functools.partial(agent_node, agent=outliner_agent, name="Outliner Agent")
writer_node = functools.partial(agent_node, agent=writer_agent, name="Writer Agent")

def editor_node(state):
  result = editor_agent.invoke(state)
  current_iterations = state.get("no_of_iterations", 0)
  N = current_iterations + 1
  return {
      "messages": [result],
      "no_of_iterations": N
  }
  
from langgraph.prebuilt import ToolNode

# LangGraph allows for us to create tool nodes
tools = [tavily, wikipedia, arxiv]
tool_node = ToolNode(tools)

from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    ToolMessage,
    AIMessage
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langgraph.graph import END, StateGraph
class AgentState(TypedDict):
  messages: Annotated[list, add_messages]
  no_of_iterations: int

def should_search(state) -> Literal["tools", "outliner"]:
    messages = state['messages']
    last_message = messages[-1]
    # If the LLM makes a tool call, then we route to the "tools" node
    if last_message.tool_calls:
        return "tools"
    # Otherwise, we stop (reply to the user)
    return "outliner"

def should_edit(state) -> Literal["writer", "__end__"]:
  messages = state['messages']
  print("Iteration number from should_edit: ", state['no_of_iterations'])
  last_message = messages[-1]

  if 'DONE' in last_message.content or state['no_of_iterations'] > MAX_ITERATIONS:
    return "__end__"

  return "writer"

MAX_ITERATIONS = 3
# Instantiate a new graph
workflow = StateGraph(AgentState)

# Add the nodes
workflow.add_node("search", search_node)
workflow.add_node("tools", tool_node)
workflow.add_node("outliner", outliner_node)
workflow.add_node("writer", writer_node)
workflow.add_node("editor", editor_node)

# Set the entrypoint as `search`
# This means that this node is the first one called
workflow.set_entry_point("search")
# Add the edges
workflow.add_conditional_edges(
    "search",
    should_search,
)
workflow.add_edge("tools", 'search')
workflow.add_edge("outliner", "writer")
workflow.add_edge("writer", "editor")
workflow.add_conditional_edges(
    "editor",
    should_edit,
    {
        "writer": "writer",
        "__end__": END
    }
)


graph = workflow.compile()

from langchain_core.messages import HumanMessage


# thread = {"configurable": {"thread_id": "1"}}

# MAX_ITERATIONS = 3

# question = "Jaki jest potencjał wykorzystania technologii generatywnych w bankowości? Zaproponuj scenariusze użycia i przykładowe uzasadnienia biznesowe."
# input_message = HumanMessage(content=question)

# for event in graph.stream({"messages": [input_message], "no_of_iterations":0}, thread, stream_mode="values"):
#     event["messages"][-1].pretty_print()