from openai import OpenAI

client = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1",
)
response = client.chat.completions.create(
    model="gemma3:1b",
    messages=[{"role": "user", "content": "Dlaczego niebo jest niebieskie?"}],
)

print(response.choices[0].message.content)
