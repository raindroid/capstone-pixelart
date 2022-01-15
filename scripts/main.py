from pixelart.utils.executer import PixelartExccuter
from pixelart.utils.params import PixelartParam
from localConfig import local_config

from pprint import pprint, pformat
from pathlib import Path
import random, sys
print(sys.version_info)
# =================================================================

# please replace following path with your configuration in the **localConfig.py** file
# DO NOT MODIFY THIS FILE DIRECTLY!!!
# path to the directory containing blender executable
blender_dir = local_config['blender_dir']
# path to the directory containing PixelArt project
pixelart_path = Path(local_config['pixelart_path'])


# =================================================================
# ================= START PixelArt ================================

print("Started executing pixel art")

# load configuration file
params = PixelartParam(str(pixelart_path / "models/params.json"))
script_templace_path = str(
    pixelart_path / "scripts/pixelart/blend/sample.py.template"
)
script_path = str(pixelart_path / "work/sample.py")

# create new working directory
(pixelart_path / "work").mkdir(parents=True, exist_ok=True)


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
        "pixelart_path": str(pixelart_path).replace('\\', '/'),
        "output_path": str(params.generator['output_path']).replace('\\', '/'),
        "settings": pformat(params.generator['settings'], width=80),
        "camera_param": pformat(params.camera, width=80),
        "objects_param": pformat(object_param, width=80),
        "scene_param": pformat(scene_param, width=80)}}

    with open(script_templace_path, "r") as tempfile, open(script_path, "w") as outfile:
        for line in tempfile:
            for replacement in configs["replacement"].items():
                key = f"__template_{replacement[0]}"
                value = replacement[1]
                if key in line:
                    line = line.replace(key, value)
            outfile.write(line)

    exe = PixelartExccuter(
        blender_dir,
        script_path,
    )
    exe.run()
    exe.wait()
