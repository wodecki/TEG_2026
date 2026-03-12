import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)
print(os.getenv("DEEPSEEK_API_KEY"))
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "Why is the sky blue?"}],
)

print(response.choices[0].message.content.strip())
