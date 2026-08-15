import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    print("❌ API key not found!")
    exit()

client = Anthropic(api_key=api_key)

message = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=200,
    messages=[
        {
            "role": "user",
            "content": "Write a one sentence professional career objective for a software engineering student."
        }
    ]
)

print("\nClaude response:\n")
print(message.content[0].text)