import os
import json
import requests
from dotenv import load_dotenv
from wand.image import Image
from xai_sdk.chat import tool

url = "https://google.serper.dev/images"
load_dotenv()

def download_image(url: str, id: str) -> str:
    headers = {
        'User-Agent': 'curl/7.68.0 Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': '*/*',
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            with Image(blob=response.content) as img:
                img.save(filename=id)
            print(f"Image saved successfully as {id}")
            return True
        else:
            print(f"Failed to download image. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"An error occurred: {e}")

def image_search(id: str, query: str) -> str:
    payload = json.dumps({"q": query})
    headers = {
      'X-API-KEY': os.getenv("SERPERDEV_API_KEY"),
      'Content-Type': 'application/json'
    }

    count = 0
    result = 'Failed to download images'
    try:
        response = requests.request("POST", url, headers=headers, data=payload, timeout=10)
    except Exception as e:
        print(f"Error: {e}")
    else:    
        response = json.loads(response.text)
        images = response['images']

        for i, image in enumerate(images):
            image_url = image['imageUrl']
            print(f"i: {i}, image_url:{image_url}")
            if download_image(url=image_url, id=f'tmp/IS_{id}_{count}.png') is True:
                count = count + 1
            if count == 2:
                break

        if count > 1:
            result = 'Successfully downloaded the images.'

    return result, count

tool_definitions = [
    tool(
        name="image_search",
        description="Search from an image on the web.",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The image query."},
            },
            "required": ["query"],
        }
    ),
]