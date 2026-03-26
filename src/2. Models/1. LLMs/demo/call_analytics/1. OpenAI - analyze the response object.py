#!/usr/bin/env python3
"""
OpenAI Response Object Analysis Demo

Demonstrates how to inspect the OpenAI API response object:
metadata, usage stats, and content extraction.

Required environment variables:
- OPENAI_API_KEY: Your OpenAI API key
"""
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-5-nano",
    messages=[
        {"role": "system", "content": "You are a helpful assistant who explains concepts clearly and concisely."},
        {"role": "user", "content": "Why is the sky blue?"},
    ],
)

# Extract and display the answer
answer = response.choices[0].message.content.strip()
print(answer)

# Analyze the response object structure
print("\n=== Response Object Analysis ===\n")

print(f"1. Response Object Type:\n   {type(response)}\n")
print(f"2. Response ID:\n   {response.id}\n")
print(f"3. Model Used:\n   {response.model}\n")
print(f"4. Full Response Object:\n   {response}\n")
print(f"5. Choices Array:\n   {response.choices}\n")
print(f"6. First Choice Object:\n   {response.choices[0]}\n")
print(f"7. Message Object:\n   {response.choices[0].message}\n")
print(f"8. Message Content:\n   {response.choices[0].message.content}\n")
print(f"9. Usage Statistics:\n   {response.usage}\n")

# Detailed usage breakdown
if response.usage:
    print("=== Detailed Usage Statistics ===")
    print(f"Prompt tokens:     {response.usage.prompt_tokens}")
    print(f"Completion tokens: {response.usage.completion_tokens}")
    print(f"Total tokens:      {response.usage.total_tokens}")

    details = getattr(response.usage, "completion_tokens_details", None)
    if details:
        print(f"Reasoning tokens:  {details.reasoning_tokens}")
        print(f"Audio tokens:      {details.audio_tokens}")