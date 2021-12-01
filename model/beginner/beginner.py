import sys, os, importlib
from os import path

VERSION = '0.0.1'

# NOTE configure the pixelart directory
dir_path = path.dirname(path.realpath(__file__))
top_dir = path.dirname(path.dirname(path.dirname(dir_path)))
scripts_dir = path.join(top_dir, 'scripts')
print(f'{scripts_dir}')
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)
from pixelart import libpixelart

# force reload the pixelart library
importlib.reload(libpixelart)

if __name__ == "__main__":

    output_folder = path.join(top_dir, 'render')
    if not path.exists(output_folder):
        os.makedirs(output_folder)

    params = {
    }
    libpixelart.pixelart_test(params, limit=2, output_folder=output_folder)