import os
from dotenv import load_dotenv

from xai_sdk import Client
from xai_sdk.chat import user, system

load_dotenv()

client = Client(
  api_key=os.getenv("XAI_API_KEY"),
  timeout=3600,
)

with open('system_prompt.md', 'r', encoding='utf-8') as file:
  system_prompt = file.read()

chat = client.chat.create(model="grok-4")
chat.append(system(system_prompt))
chat.append(user("Create a short story about Elon Musk and Harry Potter."))

response = chat.sample()
print(response.content)