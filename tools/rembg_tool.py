from rembg import remove

input_path = 'tesla_roadster_old.jpeg'
output_path = 'output1.jpg'

with open(input_path, 'rb') as i:
    with open(output_path, 'wb') as o:
        input_data = i.read()
        output_data = remove(input_data)
        o.write(output_data)