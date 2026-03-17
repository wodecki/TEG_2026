#!/usr/bin/env python3
"""
Claude (Anthropic) Simple Question Demo

This script demonstrates basic usage of the Anthropic Claude API to ask questions
and analyze the response structure. It compares the Claude API structure with OpenAI.

Required environment variables:
- ANTHROPIC_API_KEY: Your Anthropic API key
"""

from dotenv import load_dotenv
import os
import textwrap
import anthropic

# Load environment variables from .env file
load_dotenv(override=True)

# Initialize the Anthropic client with API key from environment
api_key = os.getenv('ANTHROPIC_API_KEY')

client = anthropic.Anthropic(api_key=api_key)

# Setup the system prompt and question
prompt = """
You are a friendly assistant answering users' questions. You respond in corporate slang with many anglicisms."""

question = "Why is the sky blue?"

# Make the API call to Claude
response = client.messages.create(
    model="claude-sonnet-4-20250514",  # Remember to update to current model
    max_tokens=1000,
    temperature=1,
    system=prompt,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": question
                }
            ]
        }
    ]
)

# Display the response content
print("=== Claude Response ===")
print("Raw content object:")
print(response.content)
print()

# Extract the text content
answer = response.content[0]
print("First content block:")
print(answer)
print()

# Get the actual text
answer_text = response.content[0].text
print(textwrap.fill(answer_text, width=80))


# Analyze the response object structure
print("=== Response Object Analysis ===")
print()

print("1. Response Object Type:")
print(f"   {type(response)}")
print()

print("2. Full Response Object:")
print(f"   {response}")
print()

print("3. Model Used:")
print(f"   {response.model}")
print()

print("4. Content Array:")
print(f"   {response.content}")
print()

print("5. First Content Block Text:")
print(f"   {response.content[0].text}")
print()

print("6. Usage Statistics:")
print(f"   {response.usage}")
print()

# Display usage statistics in a readable format
if response.usage:
    print("=== Detailed Usage Statistics ===")
    print(f"Input tokens: {response.usage.input_tokens}")
    print(f"Output tokens: {response.usage.output_tokens}")
    total = response.usage.input_tokens + response.usage.output_tokens
    print(f"Total tokens: {total}")

print("\n" + "="*60)
print("Note: Claude API structure differs from OpenAI:")
print("- Uses 'messages.create()' instead of 'chat.completions.create()'")
print("- Content is in 'content[0].text' instead of 'choices[0].message.content'")
print("- System prompt is a separate parameter, not part of messages")
print("- Usage statistics have different field names")
