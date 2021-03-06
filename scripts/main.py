from pixelart.utils.executer import PixelartExccuter
from pixelart.utils.params import PixelartParam
from pixelart.utils.post_render import generate_mask_bbox_and_check_small
from pixelart.utils.arguments import get_arguments
from localConfig import local_config

from pprint import pprint, pformat
from pathlib import Path
import random
import shutil
import json
import progressbar

# =================================================================

# please replace following path with your configuration in the **localConfig.py** file
# DO NOT MODIFY THIS FILE DIRECTLY!!!
args = get_arguments()
# path to the directory containing blender executable
blender_dir = local_config['blender_dir'] if str(
    args.blender) == '$config' else args.blender
# path to the directory containing PixelArt project
pixelart_path = Path(local_config['pixelart_path']) if str(
    args.path) == '$config' else args.path
print(
    f"Running PixelArt from path {pixelart_path}, with blender {blender_dir} .")

# =================================================================
# ================= START PixelArt configure setup ================
debug_mode = args.debug
print(f"PROGRESS: Started executing pixel art")
print(f"INFO: debug_mode: {debug_mode}")

# load configuration file
params = PixelartParam(str(pixelart_path / args.params_file))
script_templace_path = str(pixelart_path / args.template_scipt_file)

work_path = pixelart_path / args.work
output_path = pixelart_path / (params.generator['output_path']if args.output == '$params' else args.output)
if not args.post_process:
    # clear output output folders
    if work_path.exists() and work_path.is_dir():
        shutil.rmtree(work_path)
    if output_path.exists() and output_path.is_dir():
        shutil.rmtree(output_path)

    # create new working directory
    work_path.mkdir(parents=True, exist_ok=True)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"INFO: Created working directory at {work_path}")
    print(f"INFO: Created output directory at {output_path}")

# =================================================================
# ================== START random rendering =======================
if not args.post_process:
    config_count = params.generator['config_count'] if args.num_of_config == 0 else args.num_of_config
    object_count = params.generator['object_count'] if str(
        args.range_of_objects) == str([0]) else args.range_of_objects
    image_count = params.generator['image_count'] if str(
        args.range_of_images) == str([0]) else args.range_of_images
    use_gpu = args.use_gpu
    print(f"INFO: Rendering will {'try to' if use_gpu else 'not'} use GPU")
    print(f"INFO: Configuration count: {config_count}")
    print(f"INFO: Object count (range): {object_count}")
    print(f"INFO: Images range: {image_count}")

    for i in progressbar.progressbar(range(config_count), redirect_stdout=True):

        # random select some objects within the given count range
        object_list = list(params.objects.keys())
        random.shuffle(object_list)
        object_list = object_list[:random.randint(*object_count)]
        object_param = {}
        for key in object_list:
            object_param[key] = params.objects[key]

        # random select one scene
        scene = random.choice(list(params.scenes.keys()))
        scene_param = params.scenes[scene].copy()
        scene_param['collection'] = scene

        # log out detail
        print(
            f"INFO: Created configuration with scene {scene} and objects {', '.join(object_list)}")

        # generate new configuration
        configs = {"replacement": {
            "config_i": str(i),
            "debug": str(debug_mode),
            "pixelart_path": str(pixelart_path).replace('\\', '/'),
            "output_path": str(output_path).replace('\\', '/'),
            "work_path": str(work_path).replace('\\', '/'),

            "settings": pformat({**params.generator['settings'], **{
                "image_count": image_count, "GPU": use_gpu}}, width=80),
            "camera_param": pformat(params.camera, width=80),
            "objects_param": pformat(object_param, width=80),
            "scene_param": pformat(scene_param, width=80)}}

        script_directory = str(pixelart_path / f"work/sample_config_{i}.py")
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
        exe.wait(work_path / f"generator_config_{i}.log")


# =================================================================
# ========= Post Processing (bbox and mask generation) ============
print("PROGRESS: Started post-processing")
params_json = output_path / 'dataset.json'
params_best_json = output_path / 'dataset_best.json'
params_more_json = output_path / 'dataset_detail.json'

with open(params_json, 'r') as param:
    dataset = json.load(param)

updated_dataset = []
for i in progressbar.progressbar(range(len(dataset)), redirect_stdout=True):
    param = dataset[i]
    new_param = []
    keep_param = True  # check if the target is too small
    for mask_param in param['masks']:
        bbox, dimension, small = generate_mask_bbox_and_check_small(
            mask_param['mask_name'], output_path)
        param.setdefault('dimension', dimension)
        mask_param['bbox'] = bbox
        if not small:
            new_param.append(mask_param)
        elif mask_param['collection'] == param['camera_settings']['focus_collection']:
            keep_param = False
            print(
                f"WARNING: Emitted image img_{param['id']}, object is way too small!")
    if keep_param:
        dataset[i]['masks'] = new_param
        updated_dataset.append(dataset[i])

print(f"INFO: Final result: we have generated {len(updated_dataset)} images")

print(f"PROGRESS: Saving complete dataset to {str(params_more_json)}")
with open(params_more_json, 'w') as param:
    json.dump(updated_dataset, param)

print(f"PROGRESS: Saving simplified dataset to {str(params_best_json)}")
for param in updated_dataset:
    param['collections'] = list(param['collections'].keys())
with open(params_best_json, 'w') as param:
    json.dump(updated_dataset, param)


# ================================================================
print("Pixelart Generator DONE!!!!!!!!!!!!!!!!!!!!!!!")
