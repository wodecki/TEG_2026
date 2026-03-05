# Chains - LangGraph Educational Examples

This project contains educational examples demonstrating graph-based workflows using LangGraph, converted from Jupyter notebooks into clean Python scripts for interactive learning.

## Project Structure

- `1_Simple graph.py` - Basic LangGraph concepts from simple graphs to ReAct patterns
- `2_parallel_processes.py` - Parallel processing with asynchronous nodes and LLM integration
- `3_map_reduce.py` - Map-reduce patterns for distributed task processing
- `pyproject.toml` - Project dependencies and configuration
- `.env` - Environment variables (create this file with your API keys)

## Setup

### Prerequisites
- Python 3.10+
- `uv` package manager

### Installation

1. Install dependencies:
```bash
uv sync
```

2. Create a `.env` file with your API keys:
```bash
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
echo "TAVILY_API_KEY=your_tavily_api_key_here" >> .env
```

## Usage

### Running Individual Scripts

Execute each script directly to see educational examples:

```bash
# Basic LangGraph concepts and ReAct patterns
uv run python "1_Simple graph.py"

# Parallel processing demonstration
uv run python "2_parallel_processes.py"

# Map-reduce pattern for distributed tasks
uv run python "3_map_reduce.py"
```

### Interactive Usage

For step-by-step exploration in Python/IPython:

```python
# Start Python shell
uv run python

# Import and run specific sections
exec(open("2_parallel_processes.py").read())
exec(open("3_map_reduce.py").read())
```

## Learning Path

The project demonstrates progressive LangGraph concepts:

### 1. Simple Graph (`1_Simple graph.py`)
- **Basic Nodes**: Functions that modify graph state
- **Edges**: Direct and conditional connections between nodes
- **State Management**: Using TypedDict for graph state
- **ReAct Pattern**: Tool-aware AI agents with reasoning

### 2. Parallel Processing (`2_parallel_processes.py`)
- **Asynchronous Execution**: Multiple nodes running concurrently
- **Real-world Integration**: Tavily web search + Wikipedia
- **LLM Synthesis**: Combining multiple data sources
- **Graph Visualization**: PNG generation with dynamic naming

### 3. Map-Reduce Pattern (`3_map_reduce.py`)
- **Dynamic Parallelization**: Using Send() for variable node counts
- **Map Phase**: Parallel joke generation on subtopics
- **Reduce Phase**: Best selection from parallel results
- **Structured Outputs**: Pydantic models for reliable data

## Key Concepts Demonstrated

- **Graph Construction**: Building workflows with StateGraph
- **Parallel Execution**: Concurrent node processing for performance
- **Conditional Routing**: Dynamic path selection based on state
- **Tool Integration**: External API integration (Tavily, Wikipedia)
- **State Aggregation**: Using `operator.add` for result collection
- **Visualization**: Graph structure rendering with Mermaid
- **Error Handling**: Robust API key validation and error reporting

## Generated Files

When running the scripts, visualization files are created:

- `2_parallel_processes_simple_graph.png` - Basic parallel flow
- `2_parallel_processes_search_graph.png` - Web search architecture
- `3_map_reduce_map_reduce_graph.png` - Map-reduce flow diagram

## Dependencies

- `langchain-openai`: OpenAI model integration
- `langchain-community`: Community tools (Wikipedia, Tavily)
- `langchain-core`: Core LangChain functionality
- `langgraph`: Graph-based workflow framework
- `tavily-python`: Web search functionality
- `wikipedia`: Wikipedia API access
- `pyppeteer`: Local graph rendering
- `python-dotenv`: Environment variable management
- `pydantic`: Structured data validation
- `pillow`: Image processing support

## Environment Variables

Required environment variables in `.env`:

```
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

## Educational Notes

This project demonstrates the evolution from basic graphs to production-ready parallel AI systems:

**Progressive Complexity:**
1. **Basic Graphs** → **Parallel Processing** → **Map-Reduce Patterns**
2. **Simple State** → **Multi-source Integration** → **Dynamic Scaling**
3. **Single LLM** → **Tool Integration** → **Distributed Tasks**

**Production Concepts:**
- **Scalability**: Parallel execution reduces response times
- **Reliability**: Proper error handling and fallbacks
- **Observability**: Graph visualization for debugging
- **Security**: Environment variable API key management

**Real-world Applications:**
- **Research Assistants**: Multi-source information gathering
- **Content Generation**: Parallel creative processes with selection
- **Data Processing**: Distributed analysis and aggregation

This progression mirrors enterprise AI development, where simple prototypes evolve into scalable, production-ready systems that can handle real-world complexity and scale.