import os
import sys
import json
import time
from pathlib import Path
from typing import Literal, Optional, Dict, Any
from dotenv import load_dotenv
from web_tool import image_search, tool_definitions
from xai_sdk import Client
from xai_sdk.chat import user, system, tool, tool_result

class Imagine:
    def __init__(self):
        self.work_dir = None
        self.client = None
        self.chat = None
        self.tools_map = {
            "image_search": image_search,
        }
        self.system_prompt = None
        self.work_dir = self.create_workdir()
        self._initialize()

    def _create_workdir(self) -> Path:
        os.makedirs('tmp', exist_ok=True)
        return Path('tmp')

    def initialize(self) -> None:
        load_dotenv()
        
        with open('imagine_prompt.md', 'r', encoding='utf-8') as file:
            self.system_prompt = file.read()
        
        self.client = Client(api_key=os.getenv("XAI_API_KEY"), timeout=64000)
        self.chat = self.client.chat.create(
            model="grok-code-fast-1",
            tools=tool_definitions,
            tool_choice="auto",
        )
        self.chat.append(system(self.system_prompt))

    def process_response(self, response) -> None:
        print(f"Response: {response.content}")
        print(f"Tool calls: {response.tool_calls}")
        print(f"Usage: {response.usage}")

        if response.tool_calls:
            for tool_call in response.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                if function_name == "image_search":
                    print(f"Query: {function_args['query']}")
                
                function_args['id'] = tool_call.id.split("_")[1]
                result = self.tools_map[function_name](**function_args)
                print(f"Result: {result}")
                
                self.chat.append(tool_result(result))
                time.sleep(1)
                return None

        return None

    def run(self, scene_prompt=""):
        self.chat.append(user(scene_prompt))    
        response = self.chat.sample()
        self.chat.append(response)
        
        self.process_response(response)
        time.sleep(1)
        return None

    def fine_tune(self, instructions):
        if instructions:
            self.run(scene_prompt=instructions)

def main():
    imagine = Imagine()
    imagine.initialize()
    imagine.run(scene_prompt="Harry Potter and Ron Weasley in a flying Tesla Roadster.")
    time.sleep(3)
    sys.stdin.flush()

    while True:
        sys.stdin.flush()
        instructions = input("Enter fine tuning instructions: ")
        print(f"instructions: {instructions}")
        imagine.fine_tune(instructions)

if __name__ == '__main__':
    main()