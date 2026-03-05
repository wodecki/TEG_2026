"""
ArXiv Server - MCP server for searching academic papers on ArXiv.
No API key required, searches the open ArXiv database.
"""

from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from xml.etree import ElementTree as ET
from datetime import datetime

# Initialize FastMCP server
mcp = FastMCP("arxiv")

# Constants
ARXIV_API_BASE = "http://export.arxiv.org/api/query"

async def make_arxiv_request(params: dict[str, Any]) -> dict[str, Any] | None:
    """Make a request to the ArXiv API with proper error handling."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(ARXIV_API_BASE, params=params, timeout=30.0)
            response.raise_for_status()
            return {"content": response.text, "status": "success"}
        except Exception as e:
            return {"content": str(e), "status": "error"}

def parse_arxiv_xml(xml_content: str) -> list[dict]:
    """Parse ArXiv XML response and extract paper information."""
    try:
        root = ET.fromstring(xml_content)
        
        # Define namespace
        ns = {'atom': 'http://www.w3.org/2005/Atom',
              'arxiv': 'http://arxiv.org/schemas/atom'}
        
        papers = []
        for entry in root.findall('atom:entry', ns):
            paper = {}
            
            # Title
            title_elem = entry.find('atom:title', ns)
            paper['title'] = title_elem.text.strip() if title_elem is not None else 'No title'
            
            # Authors
            authors = []
            for author in entry.findall('atom:author', ns):
                name_elem = author.find('atom:name', ns)
                if name_elem is not None:
                    authors.append(name_elem.text)
            paper['authors'] = ', '.join(authors) if authors else 'No authors'
            
            # Summary
            summary_elem = entry.find('atom:summary', ns)
            paper['summary'] = summary_elem.text.strip() if summary_elem is not None else 'No summary'
            
            # Published date
            published_elem = entry.find('atom:published', ns)
            if published_elem is not None:
                try:
                    date_obj = datetime.fromisoformat(published_elem.text.replace('Z', '+00:00'))
                    paper['published'] = date_obj.strftime('%Y-%m-%d')
                except:
                    paper['published'] = published_elem.text
            else:
                paper['published'] = 'Unknown'
            
            # ArXiv ID and URL
            id_elem = entry.find('atom:id', ns)
            paper['url'] = id_elem.text if id_elem is not None else 'No URL'
            
            # Extract arXiv ID from URL
            if paper['url']:
                paper['arxiv_id'] = paper['url'].split('/')[-1]
            else:
                paper['arxiv_id'] = 'Unknown'
            
            # Categories
            categories = []
            for category in entry.findall('atom:category', ns):
                term = category.get('term')
                if term:
                    categories.append(term)
            paper['categories'] = ', '.join(categories) if categories else 'No categories'
            
            papers.append(paper)
        
        return papers
    except Exception as e:
        return [{"error": f"Failed to parse XML: {str(e)}"}]

def format_paper(paper: dict) -> str:
    """Format a paper into a readable string."""
    if "error" in paper:
        return f"Error: {paper['error']}"
    
    return f"""
Title: {paper.get('title', 'No title')}
Authors: {paper.get('authors', 'No authors')}
ArXiv ID: {paper.get('arxiv_id', 'Unknown')}
Published: {paper.get('published', 'Unknown')}
Categories: {paper.get('categories', 'No categories')}
URL: {paper.get('url', 'No URL')}
Summary: {paper.get('summary', 'No summary')[:500]}{'...' if len(paper.get('summary', '')) > 500 else ''}
"""

# MCP tools are async functions that can be called by MCP clients
@mcp.tool()
async def search_papers(query: str, max_results: int = 5) -> str:
    """Search for research papers on ArXiv.

    Args:
        query: Search query string
        max_results: Maximum number of results to return (default: 5)
    """
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending"
    }
    
    response = await make_arxiv_request(params)
    
    if not response or response["status"] == "error":
        return f"Unable to search ArXiv: {response.get('content', 'Unknown error') if response else 'Request failed'}"
    
    papers = parse_arxiv_xml(response["content"])
    
    if not papers:
        return "No papers found."
    
    formatted_papers = [format_paper(paper) for paper in papers]
    return "\n---\n".join(formatted_papers)

@mcp.tool()
async def search_by_author(author: str, max_results: int = 5) -> str:
    """Search for papers by a specific author.

    Args:
        author: Author name to search for
        max_results: Maximum number of results to return (default: 5)
    """
    params = {
        "search_query": f"au:{author}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }
    
    response = await make_arxiv_request(params)
    
    if not response or response["status"] == "error":
        return f"Unable to search ArXiv: {response.get('content', 'Unknown error') if response else 'Request failed'}"
    
    papers = parse_arxiv_xml(response["content"])
    
    if not papers:
        return f"No papers found for author: {author}"
    
    formatted_papers = [format_paper(paper) for paper in papers]
    return f"Papers by {author}:\n\n" + "\n---\n".join(formatted_papers)

@mcp.tool()
async def search_by_category(category: str, max_results: int = 5) -> str:
    """Search for papers in a specific category.

    Args:
        category: ArXiv category (e.g., cs.AI, math.CO, physics.gen-ph)
        max_results: Maximum number of results to return (default: 5)
    """
    params = {
        "search_query": f"cat:{category}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate", 
        "sortOrder": "descending"
    }
    
    response = await make_arxiv_request(params)
    
    if not response or response["status"] == "error":
        return f"Unable to search ArXiv: {response.get('content', 'Unknown error') if response else 'Request failed'}"
    
    papers = parse_arxiv_xml(response["content"])
    
    if not papers:
        return f"No papers found in category: {category}"
    
    formatted_papers = [format_paper(paper) for paper in papers]
    return f"Recent papers in {category}:\n\n" + "\n---\n".join(formatted_papers)

if __name__ == "__main__":
    mcp.run(transport='stdio')