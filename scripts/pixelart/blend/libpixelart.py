
import random
import os
import uuid
from math import pi
from mathutils import Vector, Euler
from typing import Iterable, Literal, Optional, Callable, Any, Dict
import bpy
import blender_operation as blender


def randomize_list(l: Iterable) -> tuple:
    return tuple(random.uniform(*r) for r in l)


def update_camera(camera_param: Optional[Dict] = None, camera=None):
    if camera is None:
        blender.remove_object_type('CAMERA')
        camera = blender.create_camera()
        # init to default values
        camera.location = (5.6, 0, 1.12)
        camera.rotation_euler = (0, pi / 2, 0)
        camera.delta_rotation_euler = (pi / 2, 0, 0)
        camera.data.dof.use_dof = True
        camera.data.lens_unit = 'MILLIMETERS'

        return camera
    else:
        camera.location = camera_param.get('location', camera.location)
        camera.rotation_euler = camera_param.get(
            'rotation', camera.rotation_euler)
        camera.data.lens = camera_param.get('lens', camera.data.lens)
        camera.data.dof.focus_object = camera_param.get(
            'focus_object', camera.data.dof.focus_object)
        camera.data.dof.aperture_fstop = camera_param.get(
            'aperture_fstop', camera.data.dof.aperture_fstop)
        camera.delta_rotation_euler[0] = camera_param.get(
            'delta_rotation', camera.delta_rotation_euler[0])


def update_location(obj: bpy.types.Object):
    pass


def render_setup():
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.use_denoising = True
    bpy.context.scene.cycles.preview_denoiser = 'AUTO'
    bpy.context.scene.cycles.preview_denoising_start_sample = 2
    bpy.context.scene.cycles.samples = 16
    bpy.context.scene.cycles.preview_samples = 8


def render_images(camera_param: Dict, scene_param: Dict, objects_param: Dict, limit: int, render_path: str):

    area, space = blender.get_view3d()
    if not area or not space:
        return "No blender area or space available"

    # clear the result
    result = {}

    # setup initial camera
    camera = update_camera()
    bpy.context.scene.camera = camera
    space.region_3d.view_perspective = 'CAMERA'

    # start rendering preview
    blender.set_shading(space, 'RENDERED')

    # setup output files
    def generate_image_id(): return f'{uuid.uuid4().hex}.jpg'
    bpy.context.scene.render.resolution_x = 1920  # image width
    bpy.context.scene.render.resolution_y = 1080  # image height

    # setup render engine
    render_setup()

    objects_list = list(objects_param.keys())
    for i in range(limit):
        image_id = generate_image_id()
        # randomize each object

        # randome select focus_object
        focus_object = blender.get_object(
            objects_param[random.choice(objects_list)]['object'])

        # randomize the camera parameters
        camera_settings = random.choice(scene_param['camera'])
        for fstop in camera_param['fstop']:
            camera_param_random = {
                "focus_object": focus_object,
                "lens": random.choice(camera_param['lens']),
                "aperture_fstop": fstop,
                "delta_rotation": random.uniform(*camera_param['delta_rotation']),
                "location": Vector(randomize_list(camera_settings['location'])),
                "rotation": Euler(randomize_list(camera_settings['rotation']), 'XYZ'),
            }
            update_camera(camera_param_random, camera)

            # render image
            image_path = os.path.join(render_path, f'img_f{fstop:3.1f}_{image_id}')
            blender.render_image(image_path)

            break
    
    return result


def pixelart_test(params: Dict, limit: int = 10, output_folder: str = 'C:\\Users\\Rain\\Documents\\PixelArt\\render'):

    # get required object
    # same as bpy.data.objects['metarig']
    man_objs = blender.get_objects('Man', lambda obj: obj.name == 'metarig')
    if not man_objs or len(man_objs) == 0:
        return -1
    man_obj = man_objs[0]

    # setup output files
    print(f"Saving {limit} images to {output_folder}")
    image_name_format = 'image{i:04d}.jpg'

    for i in range(limit):

        origin_rotation = Euler((0, 0, 0), 'XYZ')

        # define location range
        location_ranges = ((-0.92, 3.41), (-2.21, -0.07), (0.01, 0.02))
        new_location = Vector(tuple(random.uniform(*r)
                              for r in location_ranges))

        # define rotation range
        rotation_ranges = ((-pi / 3, pi / 3), (-pi / 3, pi / 3), (-pi, pi / 2))
        new_rotation = Euler(tuple(random.uniform(*r)
                             for r in rotation_ranges), 'XYZ')
        new_rotation = Euler(tuple(random.uniform(*r)
                             for r in rotation_ranges), 'XYZ')

        # define scale range
        # assume scale XYZ in same ratio
        scale_range = (0.85, 1.2)
        new_scale = tuple([random.uniform(*scale_range)] * 3)

        man_obj.location = new_location
        man_obj.delta_rotation_euler = new_rotation if random.randint(
            0, 2) == 0 else origin_rotation
        man_obj.delta_scale = new_scale

        # set output path
        image_name = image_name_format.format(i=i)
        bpy.context.scene.render.filepath = os.path.join(
            output_folder, image_name)

        # render the image

        bpy.ops.render.render(write_still=True)

    return 0
