import os
import json
import time
import base64
import mimetypes
from pathlib import Path
from typing import Literal, Optional, Dict, Any
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

from google import genai
from google.genai import types

class Compose:
    def __init__(self):
        self.client = None
        self.chat = None 
        self.chat_config = None  
        self.images = []     
        self.work_dir = self._create_workdir()
        self._initialize()

    def _create_workdir(self) -> Path:
        os.makedirs('tmp', exist_ok=True)
        return Path('tmp')

    def _initialize(self) -> None:
        load_dotenv()
        
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        self.chat_config = types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT",],
        )

    def run(self, first_image: str, second_image: str, prompt: str = "") -> bool:

        first_image_bytes = Image.open(str(self.work_dir / f'{first_image}.png'))
        second_image_bytes = Image.open(str(self.work_dir / f'{second_image}.png')) 

        response = self.client.models.generate_content(
            model="gemini-2.5-flash-image-preview",
            contents=[first_image_bytes, second_image_bytes, prompt]
        )

        image_parts = [
            part.inline_data.data
            for part in response.candidates[0].content.parts
            if part.inline_data
        ]

        if image_parts:
            image = Image.open(BytesIO(image_parts[0]))
            path = f"CI_{first_image}_{second_image}.png"
            image.save(path)
            self.images.append(path)
            return True

        return False

if __name__ == '__main__':
    compose = Compose()
    result = compose.run(first_image='IS_03847824_0',
        second_image='IS_14113881_0',
        prompt="Add Harry and Elon from the first image inside the tesla roadster in the second image.")
    if result:
        print(f"Final result: {result}")