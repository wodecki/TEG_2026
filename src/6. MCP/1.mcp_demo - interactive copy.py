#!/usr/bin/env python3
"""
Interactive MCP Client Demo - Run section by section in Jupyter.

This script demonstrates the proper MCP (Model Context Protocol) client implementation
in an interactive format. Run each section as a separate cell.

Usage: Copy each section into separate Jupyter notebook cells
"""

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# =============================================================================
# SECTION 1: MATH SERVER DEMO
# =============================================================================
# Run this entire section in one cell

print("\nMATH SERVER - MCP CLIENT DEMO")
print("=" * 45)

# Step 1: Define server parameters
server_params = StdioServerParameters(
    command="uv",
    args=["run", "--with", "mcp>=1.2.0", "math_server/math_server.py"]
)

# Steps 2-8: Connect, initialize, and interact with server
async with stdio_client(server_params) as (read_stream, write_stream):
    async with ClientSession(read_stream, write_stream) as session:
        # Initialize the MCP connection (CRITICAL!)
        print("  🤝 Initializing MCP connection...")
        await session.initialize()
        print("  ✅ MCP initialization complete!")

        # List available tools
        tools_result = await session.list_tools()
        print(f"  🛠️  Available tools: {[tool.name for tool in tools_result.tools]}")

        # Make tool calls
        print("\n  📞 Making tool calls...")

        # Addition
        result = await session.call_tool("add", {"a": 5, "b": 3})
        print(f"  ➕ 5 + 3 = {result.content[0].text}")

        # Multiplication
        result = await session.call_tool("multiply", {"a": 7, "b": 6})
        print(f"  ✖️  7 × 6 = {result.content[0].text}")

        # Power
        result = await session.call_tool("power", {"a": 2, "b": 8})
        print(f"  🔺 2^8 = {result.content[0].text}")

        # Square root
        result = await session.call_tool("sqrt", {"a": 16})
        print(f"  √ √16 = {result.content[0].text}")

# =============================================================================
# SECTION 2: 🌤️  WEATHER SERVER DEMO (OpenWeatherMap)
# =============================================================================
# Run this entire section in one cell
# Note: Requires OPENWEATHERMAP_API_KEY in .env file

print("\n🌤️  WEATHER SERVER - MCP CLIENT DEMO")
print("=" * 45)

# Define weather server parameters
weather_params = StdioServerParameters(
    command="uv",
    args=["run", "--with", "mcp>=1.2.0", "--with", "httpx>=0.28.1", "--with", "python-dotenv>=1.0.0", "weather_server/weather.py"]
)

# Connect, initialize, and query weather
async with stdio_client(weather_params) as (read_stream, write_stream):
    async with ClientSession(read_stream, write_stream) as session:
        await session.initialize()

        # List available tools
        tools_result = await session.list_tools()
        print(f"  🛠️  Available tools: {[tool.name for tool in tools_result.tools]}")

        # Get weather by city name
        print("\n  🏙️  Getting weather for Warsaw...")
        result = await session.call_tool("get_weather_by_city", {
            "city": "Warsaw",
        })
        print(f"  📊 {result.content[0].text}")

        # Get current conditions by coordinates
        print("\n  📍 Getting current conditions for Warsaw (coordinates)...")
        result = await session.call_tool("get_current_conditions", {
            "latitude": 52.2297,
            "longitude": 21.0122
        })
        print(f"  🌡️  {result.content[0].text[:400]}...")

        # Get 5-day forecast
        print("\n  📅 Getting 5-day forecast for Warsaw...")
        result = await session.call_tool("get_forecast", {
            "latitude": 52.2297,
            "longitude": 21.0122
        })
        forecast = result.content[0].text
        print(f"  📈 {forecast[:500]}...")

# =============================================================================
# SECTION 3: 📖 WIKIPEDIA SERVER DEMO
# =============================================================================
# Run this entire section in one cell

print("\n📖 WIKIPEDIA SERVER - MCP CLIENT DEMO")
print("=" * 45)

# Define Wikipedia server parameters
wiki_params = StdioServerParameters(
    command="uv",
    args=["run", "--with", "mcp>=1.2.0", "--with", "httpx>=0.28.1", "wikipedia_server/wikipedia.py"]
)

# Connect, initialize, and get summary
async with stdio_client(wiki_params) as (read_stream, write_stream):
    async with ClientSession(read_stream, write_stream) as session:
        await session.initialize()

        # Get Wikipedia summary
        print("  🔍 Getting summary of 'Machine Learning'...")
        result = await session.call_tool("get_wikipedia_summary", {
            "title": "Machine learning"
        })

        summary = result.content[0].text
        print(f"  📄 {summary[:400]}...")