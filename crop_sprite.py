from PIL import Image
import sys

# usage:
# python3 crop_sprite.py [image] [num_frames]

img_name = sys.argv[1]
img = Image.open(img_name)
width = img.width
height = img.height
num_frames = int(sys.argv[2])
diff = height / num_frames

for i in range(num_frames):
    filename = img_name[:-4] + str(i) + img_name[-4:]
    crop_box = (0,0, width, height - i * diff)
    cropped_img = img.crop(crop_box)
    cropped_img.save(filename)