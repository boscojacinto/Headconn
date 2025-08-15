import os
import base64
from dotenv import load_dotenv

from xai_sdk import Client
from xai_sdk.chat import user, system, image

load_dotenv()

client = Client(
  api_key=os.getenv("XAI_API_KEY"),
  timeout=3600,
)

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

  return encoded_string

base64_image = encode_image('docs/ron-and-harry-in-the-flying-car.jpg')

with open('system_prompt.md', 'r', encoding='utf-8') as file:
  system_prompt = file.read()

chat = client.chat.create(model="grok-4")
# chat.append(system(system_prompt))
# chat.append(user("Create a short script about Elon Musk and Harry Potter."))

chat.append(
    user(
        "What's in this image?",
        image(image_url=f"data:image/jpeg;base64,{base64_image}", detail="low"),
    )
)

response = chat.sample()
print(response.content)
print(response.usage)

# completion_tokens: 509
# prompt_tokens: 269
# total_tokens: 980
# prompt_text_tokens: 13
# prompt_image_tokens: 256
# reasoning_tokens: 202
# cached_prompt_text_tokens: 2
