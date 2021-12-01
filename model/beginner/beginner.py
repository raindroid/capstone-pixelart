import sys

# NOTE configure the pixelart directory
pixelart_dir = 'C:\\Users\\Rain\\Documents\\PixelArt\\model'
if pixelart_dir not in sys.path:
    sys.path.append(pixelart_dir)
from pixelart.libpixelart import *


VERSION = '0.0.3'

if __name__ == "__main__":
    print(f'Version: {VERSION}')

    
    pixelart_test(10, output_folder='C:\\Users\\Rain\\Documents\\PixelArt\\render')