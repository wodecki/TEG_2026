"""
Math Server - A simple MCP server providing basic mathematical operations.
Demonstrates the FastMCP pattern for creating MCP tools.
"""

from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server - creates an MCP server named "math"
mcp = FastMCP("math")

# @mcp.tool() decorator exposes this function as an MCP tool
@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers.
    
    Args:
        a: First number
        b: Second number
    """
    return a + b

@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtract b from a.
    
    Args:
        a: First number
        b: Second number
    """
    return a - b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers.
    
    Args:
        a: First number  
        b: Second number
    """
    return a * b

@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide a by b.
    
    Args:
        a: Dividend
        b: Divisor
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

@mcp.tool()
def power(a: float, b: float) -> float:
    """Raise a to the power of b.
    
    Args:
        a: Base number
        b: Exponent
    """
    return a ** b

@mcp.tool()
def sqrt(a: float) -> float:
    """Calculate square root of a number.
    
    Args:
        a: Number to calculate square root of
    """
    if a < 0:
        raise ValueError("Cannot calculate square root of negative number")
    return a ** 0.5

@mcp.tool()
def factorial(n: int) -> int:
    """Calculate factorial of a non-negative integer.
    
    Args:
        n: Non-negative integer
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

if __name__ == "__main__":
    mcp.run(transport='stdio')