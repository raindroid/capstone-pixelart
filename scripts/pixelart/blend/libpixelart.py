import bpy
import random
import os, sys
from math import pi
from mathutils import Vector, Euler
from typing import Literal, Optional, Callable, Any, Dict

CODE_ERROR = -1
CODE_SUCCESS = 0

def get_view3d(window: bpy.types.Window=None):
    focus_window = bpy.context.window_manager.windows[0] if window == None else window
    focus_area = next(iter(area for area in focus_window.screen.areas if area.type == 'VIEW_3D'), None)
    focus_space = next(iter(space for space in focus_area.spaces if space.type == 'VIEW_3D'), None)
    return focus_area, focus_space

ShadingType = Literal['WIREFRAME', 'SOLID', 'MATERIAL', 'RENDERED']
def set_shading(space: bpy.types.Space, type: ShadingType='SOLID'):
    space.shading.type = type

def get_objects(collectionName: str, condition: Optional[Callable[[Any], Any]]=None):
    if condition:
        return list(filter(condition, bpy.data.collections.get('Man').all_objects))
    else:
        return list(bpy.data.collections.get('Man').all_objects)

def pixelart_test(params: Dict, limit: int = 10, output_folder: str = 'C:\\Users\\Rain\\Documents\\PixelArt\\render'):
    
    area, space = get_view3d()
    if not area or not space: return CODE_ERROR
    print(area, space)
    
    # use solid shading to accelerate the operations
    set_shading(space)
    
    # get required object
    man_objs = get_objects('Man', lambda obj: obj.name == 'metarig') # same as bpy.data.objects['metarig']
    if not man_objs or len(man_objs) == 0: return -1
    man_obj = man_objs[0]
    
    # get a camera as active camera for image capture
    cam_obj = bpy.data.objects['MainCamera']
    if not cam_obj: return -2
    bpy.context.scene.camera = cam_obj
    space.region_3d.view_perspective = 'CAMERA'
    # save lens info to the meta
    bpy.context.scene.render.use_stamp_lens = True
    
    # setup camera parameters
    cam = cam_obj.data
    cam.lens = 35
    cam.lens_unit = 'MILLIMETERS'
    cam.dof.focus_object = man_obj
    cam.dof.aperture_fstop = 1
    
    # setup output files
    print(f"Saving {limit} images to {output_folder}")
    image_name_format = 'image{i:04d}.jpg'
    bpy.context.scene.render.resolution_x = 1920 # image width
    bpy.context.scene.render.resolution_y = 1080 # image height

    for i in range(limit):
        
        # use solid shading to accelerate the operations
        set_shading(space)
        
        origin_rotation = Euler((0,0,0), 'XYZ')
        
        # define location range
        location_ranges = ((-0.92, 3.41), (-2.21, -0.07), (0.01, 0.02))
        new_location = Vector(tuple(random.uniform(*r) for r in location_ranges))
        
        # define rotation range
        rotation_ranges = ((-pi / 3, pi / 3), (-pi / 3, pi / 3), (-pi, pi / 2))
        new_rotation = Euler(tuple(random.uniform(*r) for r in rotation_ranges), 'XYZ')
        new_rotation = Euler(tuple(random.uniform(*r) for r in rotation_ranges), 'XYZ')
        
        # define scale range
        # assume scale XYZ in same ratio
        scale_range = (0.85, 1.2)
        new_scale = tuple([random.uniform(*scale_range)] * 3)
        
        man_obj.location = new_location
        man_obj.delta_rotation_euler = new_rotation if random.randint(0,2) == 0 else origin_rotation
        man_obj.delta_scale = new_scale
        
        # start rendering preview
        set_shading(space, 'RENDERED')
        
        # set output path
        image_name = image_name_format.format(i=i)
        bpy.context.scene.render.filepath = os.path.join(output_folder, image_name)
        
        # render the image
        
        bpy.ops.render.render(write_still = True)
    
    return CODE_SUCCESS