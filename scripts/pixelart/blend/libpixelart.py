
import random
import os
import uuid
from pprint import pprint
from math import pi
from mathutils import Vector, Euler
from typing import Iterable, Literal, Optional, Callable, Any, Dict
import bpy
import blender_operation as blender
import numpy
from inspect import currentframe, getframeinfo

def randomize_list(l: Iterable, normal: bool = False) -> tuple:
    if normal:
        res = []
        for r in l:
            v = None if r[0] != r[1] else r[0]
            r = sorted(list(r))
            center = (r[0] + r[1]) / 2
            scale = abs(r[1] - r[0]) / 2
            while v is None or v < r[0] or v > r[1]:
                v = numpy.random.normal(center, scale)
            res.append(v)
        return tuple(res)
    else:
        return tuple(random.uniform(*r) for r in l)


def update_camera(camera_param: Optional[Dict] = None, camera=None):
    if camera is None:
        blender.remove_object_type('CAMERA')
        camera = blender.create_camera()
        # init to default values
        camera.select_set(True)
        camera.location = (5.6, 0, 1.12)
        camera.rotation_euler = (0, pi / 2, 0)
        camera.delta_rotation_euler = (pi / 2, 0, 0)
        camera.data.dof.use_dof = True
        camera.data.lens_unit = 'MILLIMETERS'
    else:
        camera.select_set(True)
        camera.data.lens = camera_param.get('lens', camera.data.lens)
        camera.data.dof.aperture_fstop = camera_param.get(
            'aperture_fstop', camera.data.dof.aperture_fstop)

        if 'location' in camera_param:
            camera.location = Vector(camera_param['location'])
        if 'rotation' in camera_param:
            camera.rotation_euler = Euler(camera_param['rotation'], 'XYZ')
        if 'delta_rotation' in camera_param:
            camera.delta_rotation_euler = Euler(
                camera_param['delta_rotation'], 'XYZ')
        if 'focus_object' in camera_param:
            camera.data.dof.focus_object = blender.get_object(
                camera_param.get('focus_object'))

    bpy.ops.object.select_all(action='DESELECT')
    return camera


def update_transform(collection: str, object_name: str, params: Dict[str, Any]) -> None:
    # get object and select for transformations
    target = blender.get_check_object(object_name, collection)
    # this is necessary for transformations to take effect immediately
    target.select_set(True)

    # apply transformations
    if 'location' in params:
        target.delta_location = Vector(params['location'])
    if 'rotation' in params:
        target.delta_rotation_euler = Euler(params['rotation'], 'XYZ')
    if 'scale' in params:
        target.delta_scale = Vector(params['scale'])

    bpy.ops.object.select_all(action='DESELECT')


def update_bones(collection: str, object_name: str, params: Dict[str, Any]) -> None:
    # get object and select for transformations
    target = blender.get_check_object(object_name, collection)
    # this is necessary for transformations to take effect immediately
    target.select_set(True)

    # apply transformations
    for bone_name, location in params['locations'].items():
        target.pose.bones[bone_name].location = Vector(location)

    for bone_name, rotation in params['rotations'].items():
        target.pose.bones[bone_name].rotation_euler = Euler(rotation, 'XYZ')
        
    bpy.ops.object.select_all(action='DESELECT')


def render_setup(production: bool = True) -> None:
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.use_denoising = True
    bpy.context.scene.cycles.preview_denoiser = 'AUTO'
    bpy.context.scene.cycles.use_preview_denoising = True
    if production:
        bpy.context.scene.render.resolution_x = 1920  # image width
        bpy.context.scene.render.resolution_y = 1080  # image height
        bpy.context.scene.cycles.preview_denoising_start_sample = 4
        bpy.context.scene.cycles.samples = 128
        bpy.context.scene.cycles.preview_samples = 32
    else:
        bpy.context.scene.render.resolution_x = 960  # image width
        bpy.context.scene.render.resolution_y = 540  # image height
        bpy.context.scene.cycles.preview_denoising_start_sample = 1
        bpy.context.scene.cycles.samples = 12
        bpy.context.scene.cycles.preview_samples = 4


def render_images(camera_param: Dict, scene_param: Dict, objects_param: Dict,
                  settings: Dict, render_path: str, work_directory: str,
                  debug: bool = False):

    area, space = blender.get_view3d()
    if not area or not space:
        return "No blender area or space available"

    # clear the result
    result = []

    # setup initial camera
    camera = update_camera()
    bpy.context.scene.camera = camera
    space.region_3d.view_perspective = 'CAMERA'

    # start rendering preview
    blender.set_shading(space, 'RENDERED')

    # setup output files
    def generate_image_id(): return f'{uuid.uuid4().hex}'

    # setup render engine
    render_setup(not debug)

    objects_list = list(objects_param.keys())
    render_count = 0
    overlap_retry_count = 0
    while render_count < settings['image_limit']:
        image_id = generate_image_id()
        # initial overlap detection list
        overlap_detectable = []
        overlap = False

        for object in scene_param.get('overlap_detectable', []):
            overlap_detectable.append(blender.get_check_object(
                object, scene_param['collection']))

        # randomize each object
        res_param = {}
        for collection_i, collection_name in enumerate(objects_list):
            res_param[collection_name] = {
                "transformations": {},
                "bones": {}
            }
            if overlap:
                break
            for _ in range(settings['overlap_object_retry_limit']):
                # initially no overlap overwise we would be broken out earilier (entry the loop)
                # reset overlap flag and retry (continue looping)
                overlap = False

                for object_name, object_param in objects_param[collection_name]['transformations'].items():
                    trans_param = {}

                    # generate random transformations
                    if 'rotation' in object_param['delta_transformation']:
                        trans_param['rotation'] = randomize_list(
                            object_param['delta_transformation']['rotation'], normal=True)
                    if 'scale' in object_param['delta_transformation']:
                        trans_param['scale'] = tuple(
                            [random.uniform(*object_param['delta_transformation']['scale'])] * 3)

                    # generate random location
                    center = object_param.get('center_offset', [0, 0, 0])
                    random_location = randomize_list(
                        scene_param['region'], normal=True)
                    trans_param['location'] = tuple(
                        [random_location[i] - center[i] for i in range(3)])

                    # update locations
                    update_transform(collection_name, object_name, trans_param)
                    res_param[collection_name]['transformations'][object_name] = trans_param

                # generate params for bones
                for object_name, object_param in objects_param[collection_name]['bones'].items():
                    bones_param = {"rotations": {}, "locations": {}}
                    for __ in range(settings['bone_trans_retry_limit']):
                        overlap = True
                        # generate random location
                        for bone, bone_param in object_param.get('locations', []).items():
                            normal = len(bone_param) >= 4 and bone_param[3] == 1
                            bones_param['locations'][bone] = randomize_list(bone_param[:3], normal=normal)

                        # generate random rotations
                        for bone, bone_param in object_param.get('rotations', []).items():
                            normal = len(bone_param) >= 4 and bone_param[3] == 1
                            bones_param['rotations'][bone] = randomize_list(bone_param[:3], normal=normal)
                        
                        # overlap/condition detection
                        condition_pass = True
                        for condition in object_param['conditions']:
                            if not eval(condition):
                                condition_pass = False
                                break
                        if condition_pass:
                            overlap = False
                            break

                    # update locations
                    update_bones(collection_name, object_name, bones_param)
                    res_param[collection_name]['bones'][object_name] = bones_param

                # overlap detection
                for object in objects_param[collection_name].get('overlap_detectable', []):
                    if overlap:
                        break
                    try:
                        detectable = blender.get_check_object(object, collection_name)
                    except Exception as e:
                        print(
                            f"Duplication object names detected with scene collection "
                            f"{scene_param['collection']} and "
                            f"objects {', '.join(collection_name[:collection_i + 1])}")
                        raise(e)
                    for existing_object in overlap_detectable:
                        if blender.detect_overlap(existing_object, detectable, debug=debug):
                            overlap = True
                            break

                if not overlap:
                    break   # we tried and found a non-overlap solution            
            
            # update overlap detectable objects
            overlap_detectable.extend(
                object_param.get('overlap_detectable', []))
            
        # overlap detection result
        if overlap:
            overlap_retry_count += 1
            if overlap_retry_count >= settings['overlap_retry_limit']:
                overlap_retry_count = 0
                render_count += 1  # give up on this try
            if debug:
                blender.save_as_mainfile(
                    directory=work_directory, filename=f"overlap_id_{image_id}")
            continue
        print(f"Found possible solutions for id {image_id}")

        # randome select focus_object
        focus_object = objects_param[random.choice(objects_list)]['focus']

        # randomize the camera parameters
        obj_in_camera = False
        camera_res_param = {}
        for _ in range(settings['camera_retry_limit']):
            camera_settings = random.choice(scene_param['camera'])
            camera_res_param = {
                "focus_object": focus_object,
                "lens": random.choice(camera_param['lens']),
                "location": randomize_list(camera_settings['location'], normal=True),
                "rotation": randomize_list(camera_settings['rotation'], normal=True),
                "delta_rotation": randomize_list(camera_settings['delta_rotation'], normal=True),
            }
            update_camera(camera_res_param, camera) # preset the camera parameters
            obj_in_camera = blender.is_object_in_camera(camera, focus_object)
            if obj_in_camera:
                break
            else:
                print(f"Focused object is not in frame (id {image_id}), retry...")
        
        if not obj_in_camera:
            continue
        
        render_count += 1
        result.append({'camera_settings': camera_res_param,
                       'images': []})

        # test with all f_stop values
        for fstop in camera_param['fstop']:
            camera_res_param["aperture_fstop"] = fstop
            update_camera(camera_res_param, camera)

            # render image
            file_name = f'img_{image_id}_f{fstop:3.1f}'
            image_path = os.path.join(render_path, file_name)
            blender.render_image(image_path, work_directory)

            result[-1]['images'].append({
                'fstop': fstop,
                'filename': file_name
            })

            if debug:
                blender.save_as_mainfile(
                    directory=work_directory, filename=f"id_{image_id}")
                break

    return result
