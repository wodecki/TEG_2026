import os

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

from langchain_core.tools import tool

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
os.environ["OPENWEATHERMAP_API_KEY"] = os.getenv("OPENWEATHERMAP_API_KEY")

tavily = TavilySearchResults(max_results=5)
weather = load_tools(["openweathermap-api"])[0]
wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
arxiv = load_tools(["arxiv"])[0]

@tool
def multiply(a: int, b: int) -> int:
    """Multiply a and b.

    Args:
        a: first int
        b: second int
    """
    print("Multiplying", a, b)
    return a * b

@tool
def add(a: int, b: int) -> int:
    """Add a and b.
    Args:
        a: first int
        b: second int
    """
    print("Adding", a, b)
    return a + b

@tool
def subtract(a: int, b: int) -> int:
    """Subtract a and b.
    Args:
        a: first int
        b: second int
    """
    print("Subtracting", a, b)
    return a - b

@tool
def divide(a: int, b: int) -> int:
    """Divide a and b.
    Args:
        a: first int
        b: second int
    """
    print("Dividing", a, b)
    return a / b

@tool
def power(a: int, b: int) -> int:
    """Power a and b.
    Args:
        a: first int
        b: second int
    """
    print("Powering", a, b)
    return a ** b

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)

math_tools = [multiply, add, subtract, divide, power]
tools = [tavily, weather, wikipedia, arxiv] + math_tools

prompt = """You are a helpful assistant."""

graph = create_react_agent(
    llm,
    tools=tools,
    prompt=prompt,
)

#app = graph.compile()
# q1 = "What's 2**3?"
# q2 = "Tell me about Paris"
# q3 = "What is the weather in Paris?"
# q4 = "What are the current advances in quantum computing?"

# sessionId = "session_1"
# config = {'configurable': {'thread_id': sessionId}}

# response = graph.invoke({'messages': [('user', q4)]}, config)

# print(response)