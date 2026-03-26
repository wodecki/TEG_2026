from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv(override=True)

client = Anthropic()
response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=1024,
    messages=[{"role": "user", "content": "What is the capital of France?"}],
)

print(response.content[0].text)
