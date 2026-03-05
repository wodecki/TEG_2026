"""
Tavily Server - MCP server providing web search capabilities.
Requires TAVILY_API_KEY environment variable.
"""

import os
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv(override=True)
# Initialize FastMCP server
mcp = FastMCP("tavily")

# Load Tavily API key from environment
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
TAVILY_API_BASE = "https://api.tavily.com"

async def make_tavily_request(endpoint: str, data: dict[str, Any]) -> dict[str, Any] | None:
    """Make a request to the Tavily API with proper error handling."""
    if not TAVILY_API_KEY:
        return None
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data["api_key"] = TAVILY_API_KEY
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{TAVILY_API_BASE}/{endpoint}", 
                json=data, 
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

def format_search_result(result: dict) -> str:
    """Format a search result into a readable string."""
    return f"""
Title: {result.get('title', 'No title')}
URL: {result.get('url', 'No URL')}
Content: {result.get('content', 'No content available')}
Score: {result.get('score', 'N/A')}
"""

# This tool requires TAVILY_API_KEY environment variable
@mcp.tool()
async def search(query: str, max_results: int = 5) -> str:
    """Search the web using Tavily API.

    Args:
        query: Search query string
        max_results: Maximum number of results to return (default: 5)
    """
    if not TAVILY_API_KEY:
        return "Tavily API key not found. Please set TAVILY_API_KEY environment variable."
    
    data = {
        "query": query,
        "max_results": max_results,
        "search_depth": "basic",
        "include_answer": True,
        "include_images": False,
        "include_raw_content": False
    }
    
    response = await make_tavily_request("search", data)
    
    if not response:
        return "Unable to perform search. Please check your query and try again."
    
    if not response.get("results"):
        return "No search results found."
    
    results = [format_search_result(result) for result in response["results"]]
    formatted_results = "\n---\n".join(results)
    
    # Include answer if available
    if response.get("answer"):
        return f"Answer: {response['answer']}\n\nSearch Results:\n{formatted_results}"
    
    return f"Search Results:\n{formatted_results}"

@mcp.tool()
async def search_news(query: str, max_results: int = 5) -> str:
    """Search for news articles using Tavily API.

    Args:
        query: Search query string  
        max_results: Maximum number of results to return (default: 5)
    """
    if not TAVILY_API_KEY:
        return "Tavily API key not found. Please set TAVILY_API_KEY environment variable."
    
    data = {
        "query": query,
        "max_results": max_results,
        "search_depth": "basic",
        "include_answer": True,
        "include_images": False,
        "include_raw_content": False,
        "days": 7  # Last 7 days for news
    }
    
    response = await make_tavily_request("search", data)
    
    if not response:
        return "Unable to perform news search. Please check your query and try again."
    
    if not response.get("results"):
        return "No news results found."
    
    results = [format_search_result(result) for result in response["results"]]
    formatted_results = "\n---\n".join(results)
    
    # Include answer if available
    if response.get("answer"):
        return f"News Summary: {response['answer']}\n\nNews Results:\n{formatted_results}"
    
    return f"News Results:\n{formatted_results}"

if __name__ == "__main__":
    mcp.run(transport='stdio')