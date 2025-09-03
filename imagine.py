import os
import sys
import json
import time
from pathlib import Path
from typing import Literal, Optional, Dict, List, Any
from dotenv import load_dotenv
from web_tool import image_search, tool_definitions
from xai_sdk import Client
from xai_sdk.chat import user, system, tool, tool_result

class Imagine:
    def __init__(self):
        self.work_dir = None
        self.client = None
        self.chat = None
        self.queries = []
        self.results = []
        self.tools_map = {
            "image_search": image_search,
        }
        self.system_prompt = None
        self.work_dir = self._create_workdir()
        self._initialize()

    def _create_workdir(self) -> Path:
        os.makedirs('tmp', exist_ok=True)
        return Path('tmp')

    def _initialize(self) -> None:
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

    def _process_response(self, response) -> None:
        print(f"Response: {response.content}")
        print(f"Tool calls: {response.tool_calls}")
        print(f"Usage: {response.usage}")
        self.results = []
        query = ""
        image_file = ""
        image_id = ""

        if response.tool_calls:
            for tool_call in response.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                if function_name == "image_search":
                    query = function_args['query']
                    print(f"Query: {query}")
                
                function_args['id'] = tool_call.id.split("_")[1]
                result, image_id = self.tools_map[function_name](**function_args)
                print(f"Result: {result}")
                if result == 'Successfully downloaded the image.':
                    image_file = f'IS_{function_args['id']}_{image_id}.png'
                    self.results.append({'complete': True, 'output': {'query': query, 'image_file': image_file}})
                else:
                    self.results.append({'complete': True})

                self.chat.append(tool_result(result))
                time.sleep(1)

        return None

    def run(self, prompt="") -> bool:
        self.chat.append(user(prompt))    
        response = self.chat.sample()
        self.chat.append(response)
        
        self._process_response(response)
        if len(self.results) != 2:
            return False
        else:
            return True

    def fine_tune(self, instructions):
        self.run(prompt=instructions)

def main():
    imagine = Imagine()
    imagine.run(prompt="Harry Potter and Ron Weasley in a flying Tesla Roadster.")
    time.sleep(3)
    sys.stdin.flush()

    while True:
        sys.stdin.flush()
        instructions = input("Enter fine tuning instructions: ")
        print(f"instructions: {instructions}")
        imagine.fine_tune(instructions)

if __name__ == '__main__':
    main()