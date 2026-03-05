#!/usr/bin/env python3
"""
OpenAI Response Object Analysis Demo

This script demonstrates how to analyze and work with the OpenAI API response object.
It shows how to access different parts of the response including metadata, usage stats,
and the actual content.

Required environment variables:
- OPENAI_API_KEY: Your OpenAI API key
"""
import textwrap
from openai import OpenAI
from dotenv import load_dotenv

# Use override=True to ensure project-specific settings take precedence
load_dotenv(override=True)

# Initialize OpenAI client - this creates our connection to the LLM service
client = OpenAI()

system_prompt = "You are a helpful assistant who explains concepts clearly and concisely."
question = "Why is the sky blue?"

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": question}
]

response = client.chat.completions.create(
    model="gpt-5-nano",
    messages=messages
)
answer = response.choices[0].message.content.strip()
print(answer)

# Analyze the response object structure
print("=== Response Object Analysis ===")
print()

print("1. Response Object Type:")
print(f"   {type(response)}")
print()

print("2. Response ID:")
print(f"   {response.id}")
print()

print("3. Model Used:")
print(f"   {response.model}")
print()

print("4. Full Response Object:")
print(f"   {response}")
print()

print("5. Choices Array:")
print(f"   {response.choices}")
print()

print("6. First Choice Object:")
print(f"   {response.choices[0]}")
print()

print("7. Message Object:")
print(f"   {response.choices[0].message}")
print()

print("8. Message Content:")
print(f"   {response.choices[0].message.content}")
print()

print("9. Usage Statistics:")
print(f"   {response.usage}")
print()

# Display usage statistics in a more readable format
if response.usage:
    print("=== Detailed Usage Statistics ===")
    print(f"Prompt tokens: {response.usage.prompt_tokens}")
    print(f"Completion tokens: {response.usage.completion_tokens}")
    print(f"Total tokens: {response.usage.total_tokens}")
    
    # Check if detailed usage information is available
    if hasattr(response.usage, 'completion_tokens_details'):
        details = response.usage.completion_tokens_details
        print(f"Reasoning tokens: {details.reasoning_tokens}")
        print(f"Audio tokens: {details.audio_tokens}")

print("\n" + "="*60)
print("Note: The response object contains rich metadata that can be used")
print("for monitoring, logging, and understanding API usage patterns.")