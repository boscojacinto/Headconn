import os
import base64
import json
from rembg import remove
from typing import Literal
from dotenv import load_dotenv
from wand.image import Image
from wand.display import display
from wand.color import Color

from xai_sdk import Client
from xai_sdk.chat import user, system, image, tool, tool_result

def remove_bg(serial_number: str):

  if serial_number == "1":
    image_path = 'docs/image_1.jpg'
    bgr_image_path = 'docs/bgr_image_1.jpg'
  elif serial_number == "2":
    image_path = 'docs/image_2.jpeg'
    bgr_image_path = 'docs/bgr_image_2.jpeg'
  else:
    return "false"

  with open(image_path, 'rb') as i:
    with open(bgr_image_path, 'wb') as o:
      image_data = i.read()
      bgr_image_data = remove(image_data)
      o.write(bgr_image_data)
      print(f"Removed bg")

  return "true"

  #return encode_image(bgr_image_path)

def resize_image(serial_number: str, width: str, height: str):
  if serial_number == "1":
    image_path = 'docs/image_1.jpg'
    rs_image_path = 'docs/rs_image_1.jpg'
  elif serial_number == "2":
    image_path = 'docs/image_2.jpeg'
    rs_image_path = 'docs/rs_image_2.jpeg'
  else:
    return "false"

  w_scale = (int(width[:-1]) / 100)
  h_scale = (int(height[:-1]) / 100)

  with Image(filename=image_path) as img:
    img.background_color = Color('transparent')
    img.resize(int(img.width * w_scale), int(img.height * h_scale))
    img.save(filename=rs_image_path)

  return "true"


tool_definitions = [
  tool(
    name="remove_bg",
    description="Removes the background in a given image",
    parameters={
      "type": "object",
      "properties": {
        "serial_number": {
          "type": "string",
          "description": "The serial number of the image",
        }
      },
      "required": ["serial_number"],
    },
  ),

  tool(
    name="resize_image",
    description="Resize a given image",
    parameters={
      "type": "object",
      "properties": {
        "serial_number": {
          "type": "string",
          "description": "The serial number of the image",
        },
        "width": {
          "type": "string",
          "description": "The desired width of the image",
        },
        "height": {
          "type": "string",
          "description": "The desired height of the image",
        }       
      },
      "required": ["serial_number", "width", "height"],
    },
  ),  
]

tools_map = {
    "remove_bg": remove_bg,
    "resize_image": resize_image,
}

load_dotenv()

client = Client(
  api_key=os.getenv("XAI_API_KEY"),
  timeout=64000,
)

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

  return encoded_string

first_image_b64 = encode_image('docs/image_1.jpg')
second_image_b64 = encode_image('docs/image_2.jpeg')

with open('system_prompt.md', 'r', encoding='utf-8') as file:
  system_prompt = file.read()


chat = client.chat.create(
    model="grok-4",
    tools=tool_definitions,
    tool_choice="auto",
)

# chat.append(system(system_prompt))
# chat.append(user("Create a short script about Elon Musk and Harry Potter."))

chat.append(
    user(
        "Resize the two images to half their original size.",
        image(image_url=f"data:image/jpeg;base64,{first_image_b64}", detail="low"),
        image(image_url=f"data:image/jpeg;base64,{second_image_b64}", detail="low"),
    )
)

response = chat.sample()
print(f"Response:{response.content}")
print(f"Tool calls:{response.tool_calls}")
print(f"Usage: {response.usage}")

if response.tool_calls:
  for tool_call in response.tool_calls:

    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)

    result = tools_map[function_name](**function_args)

    if function_name == "remove_bg":
      result = image(image_url=f"data:image/jpeg;base64,{result}", detail="low")

    #chat.append(tool_result(result))

# response = chat.sample()
# print(response.content)