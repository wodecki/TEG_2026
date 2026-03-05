"""
Wikipedia Server - MCP server for searching and retrieving Wikipedia articles.
No API key required, uses the public Wikipedia API.
"""

from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import json

# Initialize FastMCP server
mcp = FastMCP("wikipedia")

# Constants
WIKIPEDIA_API_BASE = "https://en.wikipedia.org/api/rest_v1"
WIKIPEDIA_SEARCH_BASE = "https://en.wikipedia.org/w/api.php"

async def make_wikipedia_request(url: str, params: dict = None) -> dict[str, Any] | None:
    """Make a request to Wikipedia API with proper error handling."""
    headers = {
        "User-Agent": "MCP Wikipedia Server/1.0",
        "Accept": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            if params:
                response = await client.get(url, params=params, headers=headers, timeout=30.0)
            else:
                response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

def clean_wikipedia_text(text: str) -> str:
    """Clean Wikipedia text by removing unwanted formatting."""
    # Remove multiple newlines and clean up spacing
    text = ' '.join(text.split())
    return text

# Wikipedia tools use the public Wikipedia API
@mcp.tool()
async def search_wikipedia(query: str, limit: int = 5) -> str:
    """Search Wikipedia articles.

    Args:
        query: Search query string
        limit: Maximum number of results to return (default: 5)
    """
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query,
        "srlimit": limit,
        "srprop": "snippet|titlesnippet|size|timestamp"
    }
    
    data = await make_wikipedia_request(WIKIPEDIA_SEARCH_BASE, params)
    
    if not data or "query" not in data or "search" not in data["query"]:
        return "Unable to search Wikipedia or no results found."
    
    results = data["query"]["search"]
    
    if not results:
        return f"No Wikipedia articles found for: {query}"
    
    formatted_results = []
    for result in results:
        snippet = clean_wikipedia_text(result.get("snippet", "No snippet available"))
        formatted_result = f"""
Title: {result.get('title', 'No title')}
Snippet: {snippet}
Size: {result.get('size', 'Unknown')} bytes
URL: https://en.wikipedia.org/wiki/{result.get('title', '').replace(' ', '_')}
"""
        formatted_results.append(formatted_result)
    
    return "\n---\n".join(formatted_results)

@mcp.tool()
async def get_wikipedia_summary(title: str) -> str:
    """Get a summary of a Wikipedia article.

    Args:
        title: Title of the Wikipedia article
    """
    # URL encode the title
    encoded_title = title.replace(" ", "_")
    url = f"{WIKIPEDIA_API_BASE}/page/summary/{encoded_title}"
    
    data = await make_wikipedia_request(url)
    
    if not data:
        return f"Unable to fetch summary for: {title}"
    
    if data.get("type") == "disambiguation":
        return f"'{title}' is a disambiguation page. Please be more specific with your search."
    
    if "extract" not in data:
        return f"No summary available for: {title}"
    
    extract = clean_wikipedia_text(data["extract"])
    
    result = f"""
Title: {data.get('title', title)}
Summary: {extract}
URL: {data.get('content_urls', {}).get('desktop', {}).get('page', f'https://en.wikipedia.org/wiki/{encoded_title}')}
"""
    
    # Add thumbnail if available
    if data.get("thumbnail"):
        result += f"\nThumbnail: {data['thumbnail']['source']}"
    
    return result

@mcp.tool()
async def get_wikipedia_content(title: str, section: str = None) -> str:
    """Get the full content of a Wikipedia article or specific section.

    Args:
        title: Title of the Wikipedia article
        section: Optional section number or title to retrieve specific section
    """
    # URL encode the title
    encoded_title = title.replace(" ", "_")
    
    if section:
        url = f"{WIKIPEDIA_API_BASE}/page/mobile-sections/{encoded_title}"
    else:
        url = f"{WIKIPEDIA_API_BASE}/page/html/{encoded_title}"
    
    data = await make_wikipedia_request(url)
    
    if not data:
        return f"Unable to fetch content for: {title}"
    
    if section:
        # Handle mobile sections response
        if "sections" not in data:
            return f"No sections found for: {title}"
        
        sections = data["sections"]
        if section.isdigit():
            section_num = int(section)
            if section_num < len(sections):
                section_data = sections[section_num]
                content = clean_wikipedia_text(section_data.get("text", "No content"))
                return f"Section {section_num}: {section_data.get('line', 'Unknown')}\n\n{content}"
            else:
                return f"Section {section} not found. Article has {len(sections)} sections."
        else:
            # Search for section by title
            for i, sect in enumerate(sections):
                if section.lower() in sect.get("line", "").lower():
                    content = clean_wikipedia_text(sect.get("text", "No content"))
                    return f"Section: {sect.get('line', 'Unknown')}\n\n{content}"
            return f"Section '{section}' not found."
    else:
        # Return summary since full HTML content would be too large
        return await get_wikipedia_summary(title)

@mcp.tool()
async def get_random_wikipedia() -> str:
    """Get a random Wikipedia article summary."""
    params = {
        "action": "query",
        "format": "json",
        "list": "random",
        "rnnamespace": 0,
        "rnlimit": 1
    }
    
    data = await make_wikipedia_request(WIKIPEDIA_SEARCH_BASE, params)
    
    if not data or "query" not in data or "random" not in data["query"]:
        return "Unable to fetch random article."
    
    random_page = data["query"]["random"][0]
    title = random_page["title"]
    
    # Get summary of the random page
    return await get_wikipedia_summary(title)

if __name__ == "__main__":
    mcp.run(transport='stdio')