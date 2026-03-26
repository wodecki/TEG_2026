#!/usr/bin/env python3
"""
Claude (Anthropic) Response Object Analysis Demo

Demonstrates how to inspect the Anthropic Claude API response object:
metadata, usage stats, and content extraction.

Required environment variables:
- ANTHROPIC_API_KEY: Your Anthropic API key
"""
import anthropic
from dotenv import load_dotenv

load_dotenv(override=True)

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1000,
    temperature=1,
    system="You are a friendly assistant answering users' questions. You respond in corporate slang with many anglicisms.",
    messages=[
        {"role": "user", "content": "Why is the sky blue?"},
    ],
)

# Extract and display the answer
answer = response.content[0].text
print(answer)

# Analyze the response object structure
print("\n=== Response Object Analysis ===\n")

print(f"1. Response Object Type:\n   {type(response)}\n")
print(f"2. Full Response Object:\n   {response}\n")
print(f"3. Model Used:\n   {response.model}\n")
print(f"4. Content Array:\n   {response.content}\n")
print(f"5. First Content Block Text:\n   {response.content[0].text}\n")
print(f"6. Usage Statistics:\n   {response.usage}\n")

# Detailed usage breakdown
if response.usage:
    print("=== Detailed Usage Statistics ===")
    print(f"Input tokens:  {response.usage.input_tokens}")
    print(f"Output tokens: {response.usage.output_tokens}")
    total = response.usage.input_tokens + response.usage.output_tokens
    print(f"Total tokens:  {total}")
