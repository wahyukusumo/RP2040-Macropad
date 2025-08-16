# https://github.com/todbot/circuitpython-tricks#python-using-pil--pillow
# The Python Image Library (PIL) fork pillow seems to work the best. It's unclear how to toggle compression.

from PIL import Image


size = (240, 240)
num_colors = 64
img = Image.open("myimage.jpg")
img = img.resize(size)
newimg = img.convert(mode="P", colors=num_colors)
newimg.save("myimage.bmp")
