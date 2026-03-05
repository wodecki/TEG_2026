import os

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

from langchain_core.tools import tool

from langgraph_supervisor import create_supervisor

# Load environment variables
from dotenv import load_dotenv
load_dotenv(override=True)

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

math_agent = create_react_agent(
    llm,
    tools=math_tools,
    name="math_expert",
)

tavily_agent = create_react_agent(
    llm,
    tools=[tavily],
    name="internet_search_expert",
)

wikipedia_agent = create_react_agent(
    llm,
    tools=[wikipedia],
    name="wikipedia_expert",
)
arxiv_agent = create_react_agent(
    llm,
    tools=[arxiv],
    name="science_expert",
)

weather_agent = create_react_agent(
    llm,
    tools=[weather],
    name="weather_expert",
)

workflow = create_supervisor(
    [math_agent, tavily_agent, wikipedia_agent, arxiv_agent, weather_agent],
    model=llm,
)

graph = workflow.compile()
q1 = "What's 2**3?"
q2 = "Tell me about Paris"
q3 = "What is the weather in Paris?"
q4 = "What are the current advances in quantum computing?"
q5 = "What's the square of the temperature in place where Adam Mickiewicz was born?"

response = graph.invoke({
    "messages": [
        {
            "role": "user",
            "content": q2
        }
    ]
})

print(response)