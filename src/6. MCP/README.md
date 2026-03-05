# MCP Servers Collection

A collection of Model Context Protocol (MCP) servers providing various tools for AI assistants and applications.

## Quick Start for Students

We provide two demo approaches for different use cases:

### 1. **Interactive Demo (Jupyter/Notebook)**
```bash
# Open 1.mcp_demo.py in Jupyter notebook
# Run each section (SECTION 1, 2, 3) in separate cells
```
This demonstrates MCP protocol in an interactive format. Perfect for step-by-step learning and experimentation.
- **File**: `1.mcp_demo.py`
- **Use**: Run sections individually in Jupyter or async REPL
- **Demos**: Math server, Weather server (OpenWeatherMap), Wikipedia server

### 2. **Command Line Demo (CLI)**
```bash
uv run "2.mcp_demo - CLI.py"
```
This runs all MCP demos sequentially from the command line.
- **File**: `2.mcp_demo - CLI.py`
- **Use**: Quick full demonstration of all servers
- **Demos**: Complete walkthrough of math, weather, and Wikipedia servers


**Learning Path**: Start with `2.mcp_demo - CLI.py` → Experiment with `1.mcp_demo.py` → Build your own!

## Demo Scripts Explained

### `1.mcp_demo.py` - Interactive MCP Demo 📓
- **Purpose**: Learn MCP protocol interactively
- **Approach**: Three sections that can be run independently in Jupyter cells
- **Pros**: Step-by-step execution, easy to modify and experiment
- **Cons**: Requires async-capable environment (Jupyter, IPython)
- **Best for**: Understanding MCP protocol flow, experimentation, teaching
- **Servers**: Math, Weather (OpenWeatherMap), Wikipedia

### `2.mcp_demo - CLI.py` - Command Line MCP Demo 🚀
- **Purpose**: Complete demonstration of all MCP servers
- **Approach**: Async functions with proper error handling
- **Pros**: Easy to run, shows all servers, production-ready patterns
- **Cons**: Runs all demos sequentially (takes longer)
- **Best for**: Quick overview, testing all servers, reference implementation
- **Servers**: Math, Weather (OpenWeatherMap), Wikipedia

## Overview

This repository contains five MCP servers, each providing specialized functionality:

- **math_server**: Mathematical operations and calculations
- **weather_server**: Global weather data from OpenWeatherMap API
- **tavily_server**: Web search capabilities via Tavily API
- **arxiv_server**: Academic paper search from ArXiv
- **wikipedia_server**: Wikipedia article search and retrieval

## Requirements

- Python 3.10 or higher
- `httpx` for HTTP requests
- `mcp[cli]` for MCP server functionality

## Quick Start

1. **Clone or download this repository**

2. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Set up environment variables** (create `.env` file or export):
   ```bash
   # For Tavily search server
   export TAVILY_API_KEY="your_tavily_api_key_here"
   
   # For Weather server
   export OPENWEATHERMAP_API_KEY="your_openweathermap_api_key_here"
   ```

   Or create a `.env` file in the MCP directory:
   ```
   TAVILY_API_KEY=your_tavily_api_key_here
   OPENWEATHERMAP_API_KEY=your_openweathermap_api_key_here
   ```

4. **Run demo scripts**:
   ```bash
   # Command line demo (runs all servers sequentially)
   uv run "2.mcp_demo - CLI.py"
   
   # Or run servers directly with dependencies
   uv run --with mcp --with httpx math_server/math.py
   OPENWEATHERMAP_API_KEY="your_key" uv run --with mcp --with httpx --with python-dotenv weather_server/weather.py
   ```

## Server Details

### 🔢 Math Server

**Location**: `math_server/`

**Tools**:
- `add(a, b)`: Add two numbers
- `subtract(a, b)`: Subtract b from a
- `multiply(a, b)`: Multiply two numbers
- `divide(a, b)`: Divide a by b (with zero-division protection)
- `power(a, b)`: Raise a to the power of b
- `sqrt(a)`: Calculate square root (with negative number protection)
- `factorial(n)`: Calculate factorial of non-negative integer

**Usage**:
```bash
uv run math_server/math.py
```

**Example**:
```python
# Via MCP call
{"tool": "add", "args": {"a": 5, "b": 3}}  # Returns: 8
{"tool": "power", "args": {"a": 2, "b": 10}}  # Returns: 1024
```

### 🌤️ Weather Server

**Location**: `weather_server/`

**Requirements**: `OPENWEATHERMAP_API_KEY` environment variable

**Tools**:
- `get_weather_by_city(city, country_code="")`: Get current weather for a city by name
- `get_forecast(latitude, longitude)`: Get 5-day forecast for coordinates
- `get_current_conditions(latitude, longitude)`: Get current weather conditions

**Data Source**: OpenWeatherMap API (global coverage)

**Usage**:
```bash
# Set API key first
export OPENWEATHERMAP_API_KEY="your_api_key"
uv run weather_server/weather.py
```

**Examples**:
```python
# Get weather by city name
{"tool": "get_weather_by_city", "args": {"city": "Warsaw", "country_code": "PL"}}

# Get forecast for coordinates (Warsaw)
{"tool": "get_forecast", "args": {"latitude": 52.2297, "longitude": 21.0122}}

# Get current conditions
{"tool": "get_current_conditions", "args": {"latitude": 52.2297, "longitude": 21.0122}}
```

### 🔍 Tavily Server

**Location**: `tavily_server/`

**Requirements**: `TAVILY_API_KEY` environment variable

**Tools**:
- `search(query, max_results=5)`: General web search
- `search_news(query, max_results=5)`: Search recent news articles

**Usage**:
```bash
export TAVILY_API_KEY="your_api_key"
uv run tavily_server/tavily.py
```

**Example**:
```python
{"tool": "search", "args": {"query": "latest AI developments", "max_results": 3}}
```

### 📚 ArXiv Server

**Location**: `arxiv_server/`

**Tools**:
- `search_papers(query, max_results=5)`: Search papers by keywords
- `search_by_author(author, max_results=5)`: Search papers by author name
- `search_by_category(category, max_results=5)`: Search papers by ArXiv category

**Common Categories**: `cs.AI`, `cs.LG`, `cs.CL`, `math.ST`, `physics.gen-ph`

**Usage**:
```bash
uv run arxiv_server/arxiv.py
```

**Example**:
```python
{"tool": "search_papers", "args": {"query": "transformer neural networks", "max_results": 3}}
{"tool": "search_by_category", "args": {"category": "cs.AI", "max_results": 5}}
```

### 📖 Wikipedia Server

**Location**: `wikipedia_server/`

**Tools**:
- `search_wikipedia(query, limit=5)`: Search Wikipedia articles
- `get_wikipedia_summary(title)`: Get article summary
- `get_wikipedia_content(title, section=None)`: Get full article or specific section
- `get_random_wikipedia()`: Get random article

**Usage**:
```bash
uv run wikipedia_server/wikipedia.py
```

**Example**:
```python
{"tool": "search_wikipedia", "args": {"query": "machine learning", "limit": 3}}
{"tool": "get_wikipedia_summary", "args": {"title": "Artificial intelligence"}}
```

## Running Individual Servers

Each server can be run independently using Python:

```bash
# Math operations (no API key required)
uv run math_server/math.py

# Weather data (requires OpenWeatherMap API key)
OPENWEATHERMAP_API_KEY="your_key" uv run weather_server/weather.py

# Web search (requires Tavily API key)
TAVILY_API_KEY="your_key" uv run tavily_server/tavily.py

# Academic papers (no API key required)
uv run arxiv_server/arxiv.py

# Wikipedia (no API key required)
uv run wikipedia_server/wikipedia.py
```

## Integration with MCP Clients

These servers are designed to work with MCP-compatible clients like Claude Desktop, LangChain, or custom applications.

### Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "math": {
      "command": "uv",
      "args": ["run", "/path/to/math_server/math.py"],
      "env": {}
    },
    "weather": {
      "command": "uv",
      "args": ["run", "/path/to/weather_server/weather.py"],
      "env": {
        "OPENWEATHERMAP_API_KEY": "your_api_key_here"
      }
    },
    "tavily": {
      "command": "uv",
      "args": ["run", "/path/to/tavily_server/tavily.py"],
      "env": {
        "TAVILY_API_KEY": "your_api_key_here"
      }
    },
    "arxiv": {
      "command": "uv",
      "args": ["run", "/path/to/arxiv_server/arxiv.py"],
      "env": {}
    },
    "wikipedia": {
      "command": "uv",
      "args": ["run", "/path/to/wikipedia_server/wikipedia.py"],
      "env": {}
    }
  }
}
```

## Example Workflows

### Research Workflow
1. Search Wikipedia for background information
2. Find recent papers on ArXiv
3. Search for latest news/developments via Tavily
4. Perform calculations related to findings

### Weather Planning
1. Get current conditions for cities worldwide
2. Get 5-day forecasts for travel destinations
3. Compare weather across multiple locations using coordinates

### Academic Research
1. Search ArXiv by category or author
2. Get Wikipedia summaries for unfamiliar concepts
3. Use math server for calculations in papers
4. Search web for recent developments

## Project Structure

```
MCP/
├── math_server/
│   ├── math.py
│   └── pyproject.toml
├── weather_server/
│   ├── weather.py
│   └── pyproject.toml
├── tavily_server/
│   ├── tavily.py
│   └── pyproject.toml
├── arxiv_server/
│   ├── arxiv.py
│   └── pyproject.toml
├── wikipedia_server/
│   ├── wikipedia.py
│   └── pyproject.toml
├── ref_agents/          # Original LangChain examples
├── ref_weather_server/  # Original reference implementation
└── README.md           # This file
```

## Error Handling

All servers include comprehensive error handling:

- **Network timeouts**: 30-second timeout for all HTTP requests
- **API errors**: Graceful handling of API failures
- **Input validation**: Type checking and bounds validation
- **Missing dependencies**: Clear error messages for missing requirements

## Development

### Adding New Tools

To add a new tool to any server:

1. Define the function with `@mcp.tool()` decorator
2. Add proper type hints and docstring
3. Include error handling
4. Test with the example script

### Creating New Servers

Follow the pattern established in existing servers:

1. Import `FastMCP` from `mcp.server.fastmcp`
2. Initialize with `mcp = FastMCP("server_name")`
3. Define tools with `@mcp.tool()` decorator
4. Run with `mcp.run(transport='stdio')`
5. Create corresponding `pyproject.toml`

## API Keys and Environment Variables

- **TAVILY_API_KEY**: Required for Tavily search functionality
  - Get from: https://tavily.com/
  - Used by: `tavily_server`

- **OPENWEATHERMAP_API_KEY**: Required for weather functionality
  - Get from: https://openweathermap.org/api
  - Used by: `weather_server`
  - Free tier available with 1000 calls/day

## Troubleshooting

### Common Issues

1. **"Module not found" errors**: Install dependencies with `pip install -e .` in each server directory

2. **Tavily authentication errors**: Ensure `TAVILY_API_KEY` is set correctly

3. **Weather server authentication errors**: Ensure `OPENWEATHERMAP_API_KEY` is set correctly and valid

4. **Weather server returns no data**: Check that:
   - API key is active and has available calls
   - City name is spelled correctly
   - Coordinates are valid (latitude: -90 to 90, longitude: -180 to 180)

5. **ArXiv search returns no results**: Try broader search terms or different categories

6. **Wikipedia disambiguation pages**: Use more specific article titles

### Debug Mode

Run servers with debug output:
```bash
uv run --verbose server_name/server.py
```

## References

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [MCP Quickstart Guide](https://modelcontextprotocol.io/quickstart)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)