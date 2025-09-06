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
        self.image_choice = None 
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

    def run(self, image_path: str, image_count: int, prompt: str = "") -> None:
        print(f"Reflect:query:{prompt}, image_count:{image_count}")
        images = [
            image(image_url=f"data:image/jpeg;base64,{encode_image(str(self.work_dir / f"{image_path + '_' + str(i)}") + '.png')}", detail="low")
            for i in range(image_count)
        ]
        self.chat = self.client.chat.create(model="grok-4")
        self.chat.append(system(self.system_prompt))
        self.chat.append(
            user(*images, prompt)
        )
        response = self.chat.sample()
        images_score = json.loads(response.content)
        image_1_score = int(images_score['image_1'].rstrip("%")) 
        image_2_score = int(images_score['image_2'].rstrip("%"))
        print(f"image_1_score:{image_1_score}")
        print(f"image_2_score:{image_2_score}")
        if image_1_score > image_2_score:
            self.image_choice = 0
        else:
            self.image_choice = 1

if __name__ == '__main__':
    reflect = Reflect()
    reflect.run(image_path='test_10.jpeg', prompt="Tesla Roadster parked on the street.")