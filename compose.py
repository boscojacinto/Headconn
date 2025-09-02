import os
import json
import time
from pathlib import Path
from typing import Literal, Optional, Dict, Any
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

class Compose:
    def __init__(self):
        self.client = None
        self.chat = None        
        self.tools_map = {
            "remove_bg": remove_bg,
            "crop_image": crop_image,
            "resize_image": resize_image,
            "rotate_image": rotate_image,
            "shear_image": shear_image,
            "draw_image": draw_image,
            "composite": composite,
        }
        self.system_prompt = None
        self.work_dir = self._create_workdir()
        self._initialize()

    def _create_workdir(self) -> Path:
        os.makedirs('tmp', exist_ok=True)
        return Path('tmp')

    def _initialize(self) -> None:
        load_dotenv()
        with open('compose_prompt.md', 'r', encoding='utf-8') as file:
            self.system_prompt = file.read()
        
        self.client = Client(api_key=os.getenv("XAI_API_KEY"), timeout=64000)
        self.chat = self.client.chat.create(
            model="grok-code-fast-1",
            tools=tool_definitions,
            tool_choice="auto",
        )
        self.chat.append(system(self.system_prompt))

    def run(self, finetune_inst: str = "") -> Optional[Dict[str, Any]]:
        prepare_images()
        first_image_b64 = encode_image(str(self.work_dir / '1.png'))
        second_image_b64 = encode_image(str(self.work_dir / '2.png'))

        self.chat.append(
            user(
                "`{ \"first_image\": \"1\", \"second_image\": \"2\"}`",
                image(image_url=f"data:image/jpeg;base64,{first_image_b64}", detail="low"),
                image(image_url=f"data:image/jpeg;base64,{second_image_b64}", detail="low"),
                finetune_inst
            )
        )

        response = self.chat.sample()
        self.chat.append(response)
        image_1_id = "1"
        image_2_id = "2"
        composite_done = False

        while True:
            print(f"Response:{response.content}")
            print(f"Tool calls:{response.tool_calls}")
            print(f"Usage:{response.usage}")

            if not response.tool_calls:
                break

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

                result = self.tools_map[function_name](**function_args)
                print(f"Result:{result}")

                if function_name == "composite":
                    composite_done = True
                    return json.loads(result)
                else:
                    self.chat.append(tool_result(result))

            time.sleep(1)
            if composite_done and finetune_inst:
                image_1_id = "1"
                image_2_id = "2"
                self.chat.append(user(finetune_inst))

            response = self.chat.sample()

        return None

if __name__ == '__main__':
    compose = Compose()
    result = compose.run(finetune_inst="Add Harry and Ron inside the tesla.")
    if result:
        print(f"Final result: {result}")