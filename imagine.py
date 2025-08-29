import os
import json
import time
from pathlib import Path
from typing import Literal
from dotenv import load_dotenv
from web_tool import (
    image_search,
    tool_definitions
)
from xai_sdk import Client
from xai_sdk.chat import user, system, tool, tool_result

def create_workdir():
    os.makedirs('tmp', exist_ok=True)
    return Path('tmp')

def init():
    load_dotenv()
    global client, chat, tools_map, work_dir, system_prompt
    tools_map = {
        "image_search": image_search,
    }
    work_dir = create_workdir()
    with open('imagine_prompt.md', 'r', encoding='utf-8') as file:
        imagine_prompt = file.read()
    client = Client(api_key=os.getenv("XAI_API_KEY"), timeout=64000)
    chat = client.chat.create(
        model="grok-code-fast-1",
        tools=tool_definitions,
        tool_choice="auto",
    )
    chat.append(system(imagine_prompt))

def main(scene_prompt=""):
    chat.append(user(scene_prompt))    
    response = chat.sample()
    chat.append(response)

    while True:
        print(f"Response:{response.content}")
        print(f"Tool calls:{response.tool_calls}")
        print(f"Usage:{response.usage}")
        if response.tool_calls:
            for tool_call in response.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                if function_name == "image_search":
                    print(f"Query:{function_args['query']}")
                
                function_args['id'] = tool_call.id.split("_")[1]
                result = tools_map[function_name](**function_args)
                print(f"Result:{result}")
                
                chat.append(tool_result(result))
                time.sleep(1)

        break
    return None

if __name__ == '__main__':
    init()
    main(scene_prompt="Harry Potter and Ron Weasley in a flying Tesla Roadster.")