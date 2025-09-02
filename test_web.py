import json
import requests
from wand.image import Image

url = "https://google.serper.dev/images"

def download_image(url, file_name):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with Image(blob=response.content) as img:
                img.save(filename=file_name)
            print(f"Image saved successfully as {file_name}")
        else:
            print(f"Failed to download image. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

def image_search(query: str):
    payload = json.dumps({
      "q": query
    })
    headers = {
      'X-API-KEY': '0b847742a2edfecd0db86cdc6c1a82ebb18115d1',
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    results = json.loads(response.text)
    imageUrl = results['images'][0]['imageUrl']
    print(imageUrl)
    download_image(imageUrl, 'tmp/test_1.png')

image_search("Harry Potter and Ron in a Ford Anglia, scene from the movie.")

# def search_web(query):
#     # Format the query for the URL
#     query = query.replace(' ', '+')
#     url = f"https://www.google.com/search?q={query}"
#     print(f"url:{url}")
    
#     # Set headers to mimic a browser
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
#         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
#         'Accept-Language': 'en-US,en;q=0.5',
#         'Referer': 'https://www.google.com/'
#     }
    
#     # Send HTTP request
#     response = requests.get(url, headers=headers)
#     print(f"response:{response}")
    
#     # Parse the HTML content
#     soup = BeautifulSoup(response.text, 'html.parser')
    
#     # Extract search results (example: titles of results)
#     results = []
#     for g in soup.find_all('div', class_='tF2Cxc'):  # Google's result container class
#         title = g.find('h3')
#         link = g.find('a')['href']
#         if title and link:
#             results.append({'title': title.text, 'url': link})
    
#     return results

# # Example usage
# query = "Python programming"
# results = search_web(query)
# print(f"results:{results}")
# for i, result in enumerate(results[:3], 1):  # Limit to top 3 results
#     print(f"{i}. {result['title']} - {result['url']}")