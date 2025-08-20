import json
import base64
import shutil
from rembg import remove
from wand.image import Image
from wand.display import display
from wand.color import Color

from xai_sdk.chat import tool

IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080

def remove_bg(id: str):
  image_id = "_".join(id.split("_")[:-1]) 
  print(f"remove_bg(image_id):{image_id}")

  image_path = f'tmp/{image_id}.png'

  with open(image_path, 'rb') as i:
    image_data = i.read()
    bgr_image_data = remove(image_data)

  with open(f'tmp/{id}.png', 'wb') as o:
    o.write(bgr_image_data)

  with Image(filename=f'tmp/{id}.png') as img:
    img.background_color = Color('transparent')
    bgr_image_size = {'state': "Removed background successfully"}

  return json.dumps(bgr_image_size)

def resize_image(id: str, width: str, height: str):
  image_id = "_".join(id.split("_")[:-1]) 
  print(f"resize_image(image_id):{image_id}")

  image_path = f'tmp/{image_id}.png'

  w_scale = (int(float(width)) / 100)
  h_scale = (int(float(height)) / 100)

  with Image(filename=image_path) as img:
    img.background_color = Color('transparent')
    img.resize(int(img.width * w_scale), int(img.height * h_scale))
    img.save(filename=f'tmp/{id}.png')
    rs_image_size = {'state': "Resized image successfully"}

  return json.dumps(rs_image_size)

def rotate_image(id: str, degree: str):
  image_id = "_".join(id.split("_")[:-1]) 
  print(f"rotate_image(image_id):{image_id}")

  image_path = f'tmp/{image_id}.png'

  with Image(filename=image_path) as img:
    img.background_color = Color('transparent')
    img.rotate(int(degree))
    img.save(filename=f'tmp/{id}.png')
    rt_image_size = {'state': "Rotated image successfully"}

  return json.dumps(rt_image_size)

def shear_image(id: str, x: str, y: str):
  image_id = "_".join(id.split("_")[:-1]) 
  print(f"shear_image(image_id):{image_id}")

  image_path = f'tmp/{image_id}.png'

  with Image(filename=image_path) as img:
    img.background_color = Color('transparent')
    img.shear(background='none', x=float(x), y=float(y))
    img.save(filename=f'tmp/{id}.png')
    sh_image_size = {'state': "Sheared image successfully"}

  return json.dumps(sh_image_size)

def composite(bg_id: str, fg_id: str, x: str, y: str, id: str):
  #image_id = "_".join(id.split("_")[:-1])
  print(f"composite(bg_id, fg_id, id):{bg_id, fg_id, id}")

  with Image(filename=f'tmp/{bg_id}.png') as bg_image:
      with Image(filename=f'tmp/{fg_id}.png') as fg_image:
        bg_image.composite(fg_image, left=int(x), top=int(y))          
        bg_image.save(filename=f'docs/3_{id}.png')
        cp_image_size = {'state': "Composite image created successfully",
                         'width': bg_image.width, 'height': bg_image.height}

  return json.dumps(cp_image_size)

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

  return encoded_string

def prepare_images():
  shutil.copy('docs/1.jpg', 'tmp/1.png')
  shutil.copy('docs/2.jpg', 'tmp/2.png')

  with Image(filename='tmp/1.png') as img_1, Image(filename='tmp/2.png') as img_2:
    img_1.background_color = Color('transparent')
    img_2.background_color = Color('transparent')
    
    img_1.resize(IMAGE_WIDTH, IMAGE_HEIGHT)
    img_2.resize(IMAGE_WIDTH, IMAGE_HEIGHT)

    img_1.save(filename=f'tmp/1.png')
    img_2.save(filename=f'tmp/2.png')

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

  tool(
    name="composite",
    description="Create a composite image of a background image and a foreground image",
    parameters={
      "type": "object",
      "properties": {
        "bg_id": {
          "type": "string",
          "description": "The label of the background image",
        },
        "fg_id": {
          "type": "string",
          "description": "The label of the foreground image",
        },
        "x": {
          "type": "string",
          "description": "The offset in pixels of foreground image on the x-axis",
        },
        "y": {
          "type": "string",
          "description": "The offset in pixels of foreground image on the y-axis",
        },        
      },
      "required": ["bg_id", "fg_id", "x", "y"],
    },
  ),    
]
