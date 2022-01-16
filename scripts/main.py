from pixelart.utils.executer import PixelartExccuter
from pixelart.utils.params import PixelartParam
from localConfig import local_config

from pprint import pprint, pformat
from pathlib import Path
import random
import shutil

# =================================================================

# please replace following path with your configuration in the **localConfig.py** file
# DO NOT MODIFY THIS FILE DIRECTLY!!!
# path to the directory containing blender executable
blender_dir = local_config['blender_dir']
# path to the directory containing PixelArt project
pixelart_path = Path(local_config['pixelart_path'])


# =================================================================
# ================= START PixelArt ================================
debug_mode = False
print(f"Started executing pixel art, debug_mode: {debug_mode}")

# load configuration file
params = PixelartParam(str(pixelart_path / "models/params.json"))
script_templace_path = str(
    pixelart_path / "scripts/pixelart/blend/sample.py.template"
)
script_directory = str(pixelart_path / "work/sample.py")

# clear output output folders
work_path = pixelart_path / "work"
if work_path.exists() and work_path.is_dir():
    shutil.rmtree(work_path)
output_path = pixelart_path / params.generator['output_path']
if output_path.exists() and output_path.is_dir():
    shutil.rmtree(output_path)

# create new working directory
work_path.mkdir(parents=True, exist_ok=True)
output_path.mkdir(parents=True, exist_ok=True)


for i in range(params.generator['config_count']):

    # random select some objects within the given count range
    object_list = list(params.objects.keys())
    random.shuffle(object_list)
    object_list = object_list[:random.randint(
        *params.generator['object_count'])]
    object_param = {}
    for key in object_list:
        object_param[key] = params.objects[key]

    # random select one scene
    scene = random.choice(list(params.scenes.keys()))
    scene_param = params.scenes[scene].copy()
    scene_param['collection'] = scene

    # log out detail
    print(
        f"Created configuration with scene {scene} and objects {', '.join(object_list)}")

    # generate new configuration
    configs = {"replacement": {
        "debug": str(debug_mode),
        "pixelart_path": str(pixelart_path).replace('\\', '/'),
        "output_path": str(params.generator['output_path']).replace('\\', '/'),
        "work_path": str(work_path).replace('\\', '/'),

        "settings": pformat(params.generator['settings'], width=80),
        "camera_param": pformat(params.camera, width=80),
        "objects_param": pformat(object_param, width=80),
        "scene_param": pformat(scene_param, width=80)}}

    with open(script_templace_path, "r") as tempfile, open(script_directory, "w") as outfile:
        for line in tempfile:
            for replacement in configs["replacement"].items():
                key = f"__template_{replacement[0]}"
                value = replacement[1]
                if key in line:
                    line = line.replace(key, value)
            outfile.write(line)

    exe = PixelartExccuter(
        blender_dir,
        script_directory,
    )
    exe.run()
    exe.wait()
