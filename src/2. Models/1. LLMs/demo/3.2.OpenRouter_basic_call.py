from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv(override=True)
api_key=os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=api_key,
)

completion = client.chat.completions.create(
  model="xiaomi/mimo-v2-pro",
  max_tokens=1024,
  messages=[
    {
      "role": "user",
      "content": "What is the capital of France?"
    }
  ]
)

print(completion.choices[0].message.content)
