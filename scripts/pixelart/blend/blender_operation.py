# This file contains wrapper functions of common blender functions

from typing import Literal, Optional, Callable, Any, Dict
import os
from pathlib import Path

import bpy
from mathutils.bvhtree import BVHTree

ShadingType = Literal['WIREFRAME', 'SOLID', 'MATERIAL', 'RENDERED']


def set_shading(space: bpy.types.Space, type: ShadingType = 'SOLID'):
    space.shading.type = type


def get_view3d(window: bpy.types.Window = None):
    focus_window = bpy.context.window_manager.windows[0] if window == None else window
    focus_area = next(
        iter(area for area in focus_window.screen.areas if area.type == 'VIEW_3D'), None)
    focus_space = next(
        iter(space for space in focus_area.spaces if space.type == 'VIEW_3D'), None)
    return focus_area, focus_space


def get_object(object: str):
    return bpy.data.objects[object]


def get_check_object(object: str, collection: str):
    objects = get_objects(collection, lambda obj: obj.name == object)
    if len(objects) != 1:
        raise ValueError(
            f"No object {object} found in {collection}, possibly a duplicate object name. Please check before proceed")

    return objects[0]


def get_objects(collection_name: str, condition: Optional[Callable[[Any], Any]] = None):
    if condition:
        return list(filter(condition, bpy.data.collections.get(collection_name).all_objects))
    else:
        return list(bpy.data.collections.get(collection_name).all_objects)


def remove_object(object: str) -> None:
    orig = bpy.data.objects[object]
    if orig:
        bpy.data.objects.remove(orig, do_unlink=True)


def remove_object_type(type: str = "CAMERA") -> None:
    for ob in bpy.data.objects:
        if ob.type == type:
            ob.select_set(True)
        else:
            ob.select_set(False)

    bpy.ops.object.delete()


def import_blend_model(
    filepath: str, objecttype: str, objectname: str,
):
    bpy.ops.wm.append(
        filepath=os.path.join(filepath, objecttype, objectname),
        directory=os.path.join(filepath, objecttype),
        filename=objectname,
    )


def save_as_mainfile(directory: str, filename: str = "output"):
    dir_path = Path(directory)
    # check if parent directory exists
    dir_path.mkdir(parents=True, exist_ok=True)
    # check if the file name is valid
    if not filename.endswith(".blend"):
        filename = filename + ".blend"
    # save to the directory
    bpy.ops.wm.save_as_mainfile(filepath=str(dir_path / filename))


def render_image(filename: str):
    # set output path
    bpy.context.scene.render.filepath = filename

    # render the image
    bpy.ops.render.render(write_still=True)


def create_camera(name: str = "MainCamera", dataname: Optional[str] = None):
    camera = bpy.data.cameras.new(name=name if dataname == None else dataname)
    camera_obj = bpy.data.objects.new(name, camera)
    bpy.context.scene.collection.objects.link(camera_obj)

    return camera_obj


def detect_overlap(obj1, obj2, debug=False) -> bool:
    # Get their world matrix
    mat1 = obj1.matrix_world
    mat2 = obj2.matrix_world

    # Get the geometry in world coordinates
    vert1 = [mat1 @ v.co for v in obj1.data.vertices]
    poly1 = [p.vertices for p in obj1.data.polygons]

    vert2 = [mat2 @ v.co for v in obj2.data.vertices]
    poly2 = [p.vertices for p in obj2.data.polygons]

    # Create the BVH trees
    bvh1 = BVHTree.FromPolygons(vert1, poly1)
    bvh2 = BVHTree.FromPolygons(vert2, poly2)

    # Test if overlap
    if bvh1.overlap(bvh2):
        if debug:
            print(f"Overlap detected for {obj1.name} and {obj2.name}")
        return True
    else:
        if debug:
            print(f"No overlap detected for {obj1.name} and {obj2.name}")
        return False
