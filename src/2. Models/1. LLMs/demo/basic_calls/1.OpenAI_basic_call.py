from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

client = OpenAI()
response = client.chat.completions.create(
    model="gpt-5-nano",
    messages=[{"role": "user", "content": "What is the capital of France?"}],
)

print(response.choices[0].message.content)
