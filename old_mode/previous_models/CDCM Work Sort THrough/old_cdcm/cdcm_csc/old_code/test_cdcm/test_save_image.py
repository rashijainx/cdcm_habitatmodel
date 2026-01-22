
import os
from datetime import datetime
from PIL import Image


# Define the folder where you want to save images
base_path = '/Users/rashijainx/Documents/GitHub/cdcm_csc/tests_models/image'

# Get the current date and time formatted as YYYY-MM-DD_HH-MM-SS
folder_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Combine the base path with the folder name to get the full path
folder_path = os.path.join(base_path, folder_name)

# Create the folder
os.makedirs(folder_path)

# Assuming you have an image loaded or created called 'my_image'
# For demonstration, let's create a simple image using PIL
my_image = Image.new('RGB', (100, 100), color = 'blue')

# Define the path for the image to be saved
image_path = os.path.join(folder_path, 'example_image.png')

# Save the image
my_image.save(image_path)

# print(f'Image saved to {image_path}')
