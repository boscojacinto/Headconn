import os
import json
import time
from pathlib import Path
from typing import Literal, Optional
from dotenv import load_dotenv
from xai_sdk import Client
from xai_sdk.chat import user, system, image
from image_tool import encode_image

class Reflect:
    def __init__(self):
        self.client = None
        self.chat = None
        self.system_prompt = None
        self.work_dir = self._create_workdir()
        self._initialize()

    def _create_workdir(self) -> Path:
        os.makedirs('tmp', exist_ok=True)
        return Path('tmp')

    def _initialize(self) -> None:
        load_dotenv()
        with open('reflect_prompt.md', 'r', encoding='utf-8') as file:
            self.system_prompt = file.read()
        
        self.work_dir = self._create_workdir()
        self.client = Client(api_key=os.getenv("XAI_API_KEY"), timeout=64000)
        self.chat = self.client.chat.create(model="grok-4")
        self.chat.append(system(self.system_prompt))

    def run(self, image_path: str, prompt: str = "") -> None:
        image_b64 = encode_image(str(self.work_dir / image_path))
        self.chat.append(
            user(
                image(image_url=f"data:image/jpeg;base64,{image_b64}", detail="low"),
                prompt
            )
        )
        response = self.chat.sample()
        print(f"Response:{response.content}")
        print(f"Usage:{response.usage}")

if __name__ == '__main__':
    reflect = Reflect()
    reflect.run(image_path='test_10.jpeg', prompt="Tesla Roadster parked on the street.")