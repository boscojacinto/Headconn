import json
import requests
from wand.image import Image
from xai_sdk.chat import tool

url = "https://google.serper.dev/images"

def download_image(url: str, id: str):
    headers = {
        'User-Agent': 'curl/7.68.0 Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': '*/*',
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            with Image(blob=response.content) as img:
                img.save(filename=id)
            print(f"Image saved successfully as {id}")
        else:
            print(f"Failed to download image. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

def image_search(id: str, query: str):
    payload = json.dumps({"q": query})
    headers = {
      'X-API-KEY': '0b847742a2edfecd0db86cdc6c1a82ebb18115d1',
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    results = json.loads(response.text)
    images = results['images']
    for i, image in enumerate(images):
        image_url = image['imageUrl']
        print(f"i: {i}, image_url:{image_url}")
        download_image(url=image_url, id=f'tmp/{id}_{i}.png')
        break

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