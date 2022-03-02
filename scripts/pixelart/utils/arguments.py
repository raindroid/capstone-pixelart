import argparse
from ast import Str


def get_arguments():
    parser = argparse.ArgumentParser(description="Render Image Datasets")
    parser.add_argument("-p", "--path", nargs="?", action="store",
                        default="$config", help="Path of PixelArt (or leave blank to use localConfig.py)")
    parser.add_argument("-b", "--blender", nargs="?", action="store",
                        default="$config", help="Path of blender (or leave blank to use localConfig.py)")
    parser.add_argument("-a", "--params_file", nargs="?",  action="store",
                        default="models/params.json", help="Relative path of params.json to PixelArt directory")
    parser.add_argument("-t", "--template_scipt_file", nargs="?",  action="store",
                        default="scripts/pixelart/blend/sample.py.template", help="Relative path of template script to PixelArt directory")
    parser.add_argument("-w", "--work", nargs="?", action="store",
                        default="work", help="Relative work directory (default in pixelart/work)")
    parser.add_argument("-o", "--output", nargs="?", action="store",
                        default="$params", help="Relative output directory (overwrite value in params.json)")
    parser.add_argument("-nc", "--num_of_config", nargs="?", type=int, action="store",
                        default=0, help="Number of config (overwrite value in params.json)")
    parser.add_argument("-ro", "--range_of_objects", nargs=2, type=int, action="store",
                        default=[0], help="Range of objects imported to each configuration (overwrite value in params.json)")
    parser.add_argument("-ri", "--range_of_images", nargs=2, type=int, action="store",
                        default=[0], help="Range of images generated for each configuration (overwrite value in params.json)")
    parser.add_argument("-GPU", "--use_gpu", default=False, action="store_true",
                        help="Reset the use of GPU (overwrite value in params.json)")
    parser.add_argument("-d", "--debug",
                        default=False, action="store_true", help="Debug mode")

    args = parser.parse_args()
    return args
