"""
OpenAI Function Calling Fundamentals
====================================

This script demonstrates the core concepts of OpenAI function calling:
1. How to define tools for OpenAI models
2. How the model decides when to call tools
3. How to handle tool call responses
4. Complete tool calling workflow

Key learning points:
- Tools are defined as JSON schemas wrapped in {"type": "function", ...}
- Model chooses whether to call tools based on user input
- Tool calls require manual execution and response handling
- Full conversation flow involves multiple API calls

Note on the API:
- This uses the modern `tools` / `tool_calls` interface. The older
  `functions` / `function_call` interface is deprecated and is rejected
  by newer models (e.g. the `gpt-5.x` family), which no longer accept the
  legacy `function` message role.
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

# Tool schemas that OpenAI understands.
# Each tool wraps a JSON-schema function definition in {"type": "function", ...}.
tools = [
    {
        "type": "function",
        "function": {
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
    },
    {
        "type": "function",
        "function": {
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
        },
    }
]

# ================================
# EXAMPLE 1: BASIC FUNCTION CALLING
# ================================

print("=== EXAMPLE 1: Weather Query ===")
messages = [{"role": "user", "content": "What's the weather like in Boston?"}]

response = client.chat.completions.create(
    model="gpt-5.4-mini",
    messages=messages,
    tools=tools
)

print("User:", messages[0]["content"])
print("Model response:", response.choices[0].message.tool_calls)
# Expected: Model chooses to call get_current_weather function

# ================================
# EXAMPLE 2: IRRELEVANT QUERY
# ================================

print("\n=== EXAMPLE 2: Irrelevant Query ===")
messages = [{"role": "user", "content": "Hello! How are you?"}]

response = client.chat.completions.create(
    model="gpt-5.4-mini",
    messages=messages,
    tools=tools
)

print("User:", messages[0]["content"])
print("Model response:", response.choices[0].message.content)
# Expected: Model responds normally without tool calls

# ================================
# EXAMPLE 3: FORCED FUNCTION CALLING
# ================================

print("\n=== EXAMPLE 3: Forced Function Call ===")
messages = [{"role": "user", "content": "Hello there!"}]

response = client.chat.completions.create(
    model="gpt-5.4-mini",
    messages=messages,
    tools=tools,
    tool_choice={  # Force a specific tool
        "type": "function",
        "function": {"name": "get_current_weather"}
    }
)

print("User:", messages[0]["content"])
print("Forced function call:", response.choices[0].message.tool_calls)
# Expected: Model forced to call weather function even for irrelevant query

# ================================
# EXAMPLE 4: COMPLETE FUNCTION CALLING WORKFLOW
# ================================

print("\n=== EXAMPLE 4: Complete Workflow ===")

# Step 1: User asks a question
messages = [{"role": "user", "content": "What's the weather in San Francisco and what's 2 to the power of 8?"}]

print("Step 1 - User question:", messages[0]["content"])

# Step 2: Model decides to call tools (it may request several in parallel)
response = client.chat.completions.create(
    model="gpt-5.4-mini",
    messages=messages,
    tools=tools
)

print("Step 2 - Model chooses tool calls")
response_message = response.choices[0].message

# Step 3: Execute tool calls manually
if response_message.tool_calls:
    # Add the assistant turn (which carries the tool_calls) to the conversation
    messages.append(response_message)

    # The model can request multiple tools at once, so iterate over all of them
    for tool_call in response_message.tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)

        print(f"Step 3 - Executing {function_name} with args:", function_args)

        # Call the appropriate function
        if function_name == "get_current_weather":
            function_response = get_current_weather(**function_args)
        elif function_name == "calculate_power":
            function_response = calculate_power(**function_args)

        print("Function result:", function_response)

        # Step 4: Add the tool response to the conversation, linked by tool_call_id
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": str(function_response)
        })

    # Step 5: Get final response from model
    final_response = client.chat.completions.create(
        model="gpt-5.4-mini",
        messages=messages
    )

    print("Step 5 - Final response:", final_response.choices[0].message.content)
    # Expected: Natural language response incorporating tool results

print("\n=== Key Takeaways ===")
print("1. OpenAI models can intelligently choose when to call tools")
print("2. Tool calls require manual execution - the model doesn't run them")
print("3. Tool responses must be added back to the conversation (role='tool')")
print("4. The complete workflow involves multiple API calls")
print("5. Tools are defined using JSON schema wrapped in {'type': 'function'}")