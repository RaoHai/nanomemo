import os
from openai import OpenAI

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Error: OPENAI_API_KEY environment variable not set")
    exit(1)

print(f"API Key: {api_key[:20]}...")

client = OpenAI(api_key=api_key)
print("Client initialized")

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Say hello"}],
    max_tokens=10
)
print(f"Response: {response.choices[0].message.content}")
