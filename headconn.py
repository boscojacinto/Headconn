import os
import json
import time
from pathlib import Path
from typing import Literal
from dotenv import load_dotenv
from image_tool import (
    remove_bg,
    crop_image,
    resize_image,
    rotate_image,
    shear_image,
    draw_image,
    composite,
    encode_image,
    prepare_images,
    tool_definitions
)
from xai_sdk import Client
from xai_sdk.chat import user, system, image, tool, tool_result

def create_workdir():
    os.makedirs('tmp', exist_ok=True)
    return Path('tmp')

def init():
    load_dotenv()
    global client, chat, tools_map, work_dir, system_prompt
    tools_map = {
        "remove_bg": remove_bg,
        "crop_image": crop_image,
        "resize_image": resize_image,
        "rotate_image": rotate_image,
        "shear_image": shear_image,
        "draw_image": draw_image,
        "composite": composite,
    }
    work_dir = create_workdir()
    with open('system_prompt.md', 'r', encoding='utf-8') as file:
        system_prompt = file.read()
    client = Client(api_key=os.getenv("XAI_API_KEY"), timeout=64000)
    chat = client.chat.create(model="grok-4", tools=tool_definitions, tool_choice="auto")
    chat.append(system(system_prompt))

def main(finetune_inst=""):
    prepare_images()
    first_image_b64 = encode_image(str(Path(work_dir) / '1.png'))
    second_image_b64 = encode_image(str(Path(work_dir) / '2.png'))
    chat.append(
        user(
            "`{ \"first_image\": \"1\", \"second_image\": \"2\"}`",
            image(image_url=f"data:image/jpeg;base64,{first_image_b64}", detail="low"),
            image(image_url=f"data:image/jpeg;base64,{second_image_b64}", detail="low"),
            finetune_inst
        )
    )
    response = chat.sample()
    chat.append(response)
    image_1_id = "1"
    image_2_id = "2"
    composite_done = False

    while True:
        print(f"Response:{response.content}")
        print(f"Tool calls:{response.tool_calls}")
        print(f"Usage:{response.usage}")
        if response.tool_calls:
            for tool_call in response.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                if function_name == "composite":
                    if function_args['bg_id'] == "1" and function_args['fg_id'] == "2":
                        function_args['bg_id'] = image_1_id
                        function_args['fg_id'] = image_2_id
                        function_args['id'] = tool_call.id.split("_")[1]
                    elif function_args['bg_id'] == "2" and function_args['fg_id'] == "1":
                        function_args['bg_id'] = image_2_id
                        function_args['fg_id'] = image_1_id
                        function_args['id'] = tool_call.id.split("_")[1]
                else:
                    if function_args['id'] == "1":
                        image_id = "_".join([image_1_id, tool_call.id.split("_")[1]])
                        image_1_id = image_id
                    elif function_args['id'] == "2":
                        image_id = "_".join([image_2_id, tool_call.id.split("_")[1]])
                        image_2_id = image_id
                    function_args['id'] = image_id
                result = tools_map[function_name](**function_args)
                print(f"Result:{result}")
                if function_name == "composite":
                    composite_done = True
                    return json.loads(result)
                else:
                    chat.append(tool_result(result))
            time.sleep(1)
            if composite_done and finetune_inst:
                image_1_id = "1"
                image_2_id = "2"
                chat.append(user(finetune_inst))
            response = chat.sample()
        else:
            break
    return None