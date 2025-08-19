from wand.image import Image
from rembg import remove

def remove_bg(filename, name):
  image_path = filename

  with open(image_path, 'rb') as i:
    image_data = i.read()
    bgr_image_data = remove(image_data)

  with open(f'tmp/image_{name}.png', 'wb') as o:
    o.write(bgr_image_data)

  return "Removed background successfully"

# Load the two images
remove_bg('docs/wizard.jpeg', 'a')
remove_bg('docs/rose.jpeg', 'b')

# with Image(filename='tmp/image_a.png') as img1:
#     with Image(filename='tmp/image_b.png') as img2:
#         # Ensure both images have the same height for side-by-side juxtaposition
#         if img1.height != img2.height:
#             img2.resize(width=int(img2.width * img1.height / img2.height), height=img1.height)

#         # Create a new image with width = sum of both widths and height = max height
#         with Image(width=img1.width + img2.width, height=img1.height) as result:
#             # Paste img1 on the left
#             result.composite(img1, 0, 0)
#             # Paste img2 on the right
#             result.composite(img2, img1.width, 0)
#             # Save the result
#             result.save(filename='docs/juxtaposed.png')


# Load the background image and the image to crop
with Image(filename='tmp/image_b.png') as bg_image:
    with Image(filename='tmp/image_a.png') as overlay_image:
        # Crop the overlay image (e.g., 100x100 pixels starting at (50, 50))
        #overlay_image.crop(left=50, top=50, width=100, height=100)
        
        # Place the cropped image on the background at position (x=200, y=150)
        bg_image.composite(overlay_image, left=10, top=10)
        
        # Save the result
        bg_image.save(filename='docs/juxtaposed.png')            