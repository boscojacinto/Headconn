import os
import json
import shutil
from pathlib import Path
from typing import Literal
from dotenv import load_dotenv
from tools.image_tool import remove_bg, resize_image, rotate_image, shear_image, encode_image, tool_definitions 

from xai_sdk import Client
from xai_sdk.chat import user, system, image, tool, tool_result

def create_workdir():
  os.makedirs('tmp', exist_ok=True)

  shutil.copy('docs/image_1.jpg', 'tmp/1.jpg')
  shutil.copy('docs/image_2.jpg', 'tmp/2.jpg')

  return Path('tmp')

load_dotenv()

tools_map = {
    "remove_bg": remove_bg,
    "resize_image": resize_image,
    "rotate_image": rotate_image,
    "shear_image": shear_image,
}

work_dir = create_workdir()

with open('system_prompt.md', 'r', encoding='utf-8') as file:
  system_prompt = file.read()

client = Client(api_key=os.getenv("XAI_API_KEY"), timeout=64000)

chat = client.chat.create(model="grok-4", tools=tool_definitions,
                          tool_choice="auto")

chat.append(system(system_prompt))
# chat.append(user("Create a short script about Elon Musk and Harry Potter."))

first_image_b64 = encode_image(str(Path(work_dir) / '1' / 'image.jpg'))
second_image_b64 = encode_image(str(Path(work_dir) / '2' / 'image.jpg'))

chat.append(
    user(
        "`{ \"first_image\": \"1\", \"second_image\": \"2\"}`",
        image(image_url=f"data:image/jpeg;base64,{first_image_b64}", detail="low"),
        image(image_url=f"data:image/jpeg;base64,{second_image_b64}", detail="low"),
    )
)

response = chat.sample()
print(f"Response:{response.content}")
print(f"Tool calls:{response.tool_calls}")
print(f"Usage:{response.usage}")

#chat.append(response)

if response.tool_calls:
  for tool_call in response.tool_calls:

    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)
    function_args['id'] = f"{function_args['id']}_{tool_call.id.split("_")[1]}"
    result = tools_map[function_name](**function_args)

    #chat.append(tool_result(result))
