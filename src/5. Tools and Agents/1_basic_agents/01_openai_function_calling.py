"""
OpenAI Function Calling Fundamentals
====================================

This script demonstrates the core concepts of OpenAI function calling:
1. How to define functions for OpenAI models
2. How the model decides when to call functions
3. How to handle function call responses
4. Complete function calling workflow

Key learning points:
- Functions are defined as JSON schemas
- Model chooses whether to call functions based on user input
- Function calls require manual execution and response handling
- Full conversation flow involves multiple API calls
"""

import json
import os
from openai import OpenAI
from dotenv import load_dotenv

# ================================
# SETUP AND CONFIGURATION
# ================================

load_dotenv(override=True)
client = OpenAI()

# ================================
# FUNCTION DEFINITIONS
# ================================

def get_current_weather(location, unit="fahrenheit"):
    """
    Example weather function - returns mock data for demonstration.
    In production, this would call a real weather API.
    """
    weather_info = {
        "location": location,
        "temperature": "72",
        "unit": unit,
        "forecast": ["sunny", "windy"],
    }
    return json.dumps(weather_info)

def calculate_power(base, exponent):
    """
    Simple math function for demonstration.
    """
    return base ** exponent

# Function schemas that OpenAI understands
functions = [
    {
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA",
                },
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
            },
            "required": ["location"],
        },
    },
    {
        "name": "calculate_power",
        "description": "Calculate base raised to the power of exponent",
        "parameters": {
            "type": "object",
            "properties": {
                "base": {"type": "number", "description": "The base number"},
                "exponent": {"type": "number", "description": "The exponent"},
            },
            "required": ["base", "exponent"],
        },
    }
]

# ================================
# EXAMPLE 1: BASIC FUNCTION CALLING
# ================================

print("=== EXAMPLE 1: Weather Query ===")
messages = [{"role": "user", "content": "What's the weather like in Boston?"}]

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    functions=functions
)

print("User:", messages[0]["content"])
print("Model response:", response.choices[0].message.function_call)
# Expected: Model chooses to call get_current_weather function

# ================================
# EXAMPLE 2: IRRELEVANT QUERY
# ================================

print("\n=== EXAMPLE 2: Irrelevant Query ===")
messages = [{"role": "user", "content": "Hello! How are you?"}]

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    functions=functions
)

print("User:", messages[0]["content"])
print("Model response:", response.choices[0].message.content)
# Expected: Model responds normally without function calls

# ================================
# EXAMPLE 3: FORCED FUNCTION CALLING
# ================================

print("\n=== EXAMPLE 3: Forced Function Call ===")
messages = [{"role": "user", "content": "Hello there!"}]

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    functions=functions,
    function_call={"name": "get_current_weather"}  # Force specific function
)

print("User:", messages[0]["content"])
print("Forced function call:", response.choices[0].message.function_call)
# Expected: Model forced to call weather function even for irrelevant query

# ================================
# EXAMPLE 4: COMPLETE FUNCTION CALLING WORKFLOW
# ================================

print("\n=== EXAMPLE 4: Complete Workflow ===")

# Step 1: User asks a question
messages = [{"role": "user", "content": "What's the weather in San Francisco and what's 2 to the power of 8?"}]

print("Step 1 - User question:", messages[0]["content"])

# Step 2: Model decides to call functions
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    functions=functions
)

print("Step 2 - Model chooses function calls")
response_message = response.choices[0].message

# Step 3: Execute function calls manually
if response_message.function_call:
    function_name = response_message.function_call.name
    function_args = json.loads(response_message.function_call.arguments)

    print(f"Step 3 - Executing {function_name} with args:", function_args)

    # Call the appropriate function
    if function_name == "get_current_weather":
        function_response = get_current_weather(**function_args)
    elif function_name == "calculate_power":
        function_response = calculate_power(**function_args)

    print("Function result:", function_response)

    # Step 4: Add function response to conversation
    messages.append({
        "role": "assistant",
        "content": None,
        "function_call": {
            "name": function_name,
            "arguments": response_message.function_call.arguments
        }
    })

    messages.append({
        "role": "function",
        "name": function_name,
        "content": function_response
    })

    # Step 5: Get final response from model
    final_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    print("Step 5 - Final response:", final_response.choices[0].message.content)
    # Expected: Natural language response incorporating function results

print("\n=== Key Takeaways ===")
print("1. OpenAI models can intelligently choose when to call functions")
print("2. Function calls require manual execution - the model doesn't run them")
print("3. Function responses must be added back to the conversation")
print("4. The complete workflow involves multiple API calls")
print("5. Functions are defined using JSON schema format")