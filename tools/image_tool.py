import base64
import shutil
from rembg import remove
from wand.image import Image
from wand.display import display
from wand.color import Color

from xai_sdk.chat import tool

def remove_bg(id: str):
  image_id = "_".join(id.split("_")[:-1]) 
  print(f"remove_bg(image_id):{image_id}")

  image_path = f'tmp/{image_id}.jpg'

  with open(image_path, 'rb') as i:
    image_data = i.read()
    bgr_image_data = remove(image_data)

  with open(f'tmp/{id}.png', 'wb') as o:
    o.write(bgr_image_data)

  return "Removed background successfully"

def resize_image(id: str, width: str, height: str):
  image_id = "_".join(id.split("_")[:-1]) 
  print(f"resize_image(image_id):{image_id}")

  image_path = f'tmp/{image_id}.jpg'

  w_scale = (int(width) / 100)
  h_scale = (int(height) / 100)

  with Image(filename=image_path) as img:
    img.background_color = Color('transparent')
    img.resize(int(img.width * w_scale), int(img.height * h_scale))
    img.save(filename=f'tmp/{id}.png')

  return "Resize successful"

def rotate_image(id: str, degree: str):
  image_id = "_".join(id.split("_")[:-1]) 
  print(f"rotate_image(image_id):{image_id}")

  with Image(filename=image_path) as img:
    img.background_color = Color('transparent')
    img.rotate(int(degree))
    img.save(filename=f'tmp/{id}.png')

  return "Rotated successfully"

def shear_image(id: str, x: str, y: str):
  image_id = "_".join(id.split("_")[:-1]) 
  print(f"shear_image(image_id):{image_id}")

  with Image(filename=image_path) as img:
    img.background_color = Color('transparent')
    img.shear(background='none', x=float(x), y=float(y))
    img.save(filename=f'tmp/{id}.png')

  return "Image shear successful"

def composite(bg_image: str, fg_image: str):
  with Image(filename='tmp/image_b.png') as bg_image:
      with Image(filename='tmp/image_a.png') as overlay_image:
          # Crop the overlay image (e.g., 100x100 pixels starting at (50, 50))
          #overlay_image.crop(left=50, top=50, width=100, height=100)
          
          # Place the cropped image on the background at position (x=200, y=150)
          bg_image.composite(overlay_image, left=10, top=10)
          
          # Save the result
          bg_image.save(filename='docs/juxtaposed.png')

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

  return encoded_string

tool_definitions = [
  tool(
    name="remove_bg",
    description="Removes the background in a given image",
    parameters={
      "type": "object", 
      "properties": {
        "id": {
          "type": "string",
          "description": "The label of the image",
        },        
      },
      "required": ["id"],      
    }
  ),

  tool(
    name="resize_image",
    description="Resize a given image",
    parameters={
      "type": "object",
      "properties": {
        "id": {
          "type": "string",
          "description": "The label of the image",
        },              
        "width": {
          "type": "string",
          "description": "The desired width of the image in percentage",
        },
        "height": {
          "type": "string",
          "description": "The desired height of the image in percentage",
        }       
      },
      "required": ["id", "width", "height"],
    },
  ),

  tool(
    name="rotate_image",
    description="Rotate a given image",
    parameters={
      "type": "object",
      "properties": {
        "id": {
          "type": "string",
          "description": "The label of the image",
        },              
        "degree": {
          "type": "string",
          "description": "The desired rotation in degrees",
        }
      },
      "required": ["id", "degree"],
    },
  ),

  tool(
    name="shear_image",
    description="Shear a given image along the x and y axis",
    parameters={
      "type": "object",
      "properties": {
        "id": {
          "type": "string",
          "description": "The label of the image",
        },              
        "x": {
          "type": "string",
          "description": "The amount of shear on the x-axis in decimals",
        },
        "y": {
          "type": "string",
          "description": "The amount of shear on the y-axis in decimals",
        },        
      },
      "required": ["id", "x", "y"],
    },
  ),  
]
