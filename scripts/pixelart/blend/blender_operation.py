# This file contains wrapper functions of common blender functions

from typing import Literal, Optional, Callable, Any, Dict
import os
import sys
from pathlib import Path

import bpy
from bpy import context
from mathutils.bvhtree import BVHTree
from mathutils.geometry import normal
from mathutils import Vector

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


def render_image(filename: str, work_directory: str):
    # set output path
    bpy.context.scene.render.filepath = filename
    print(f"Start rendering to filepath {filename} ...")

    # redirect output to file log temporarily
    logfile = Path(work_directory, "blender_render.log")
    open(logfile, 'a').close()
    old = os.dup(1)
    sys.stdout.flush()
    os.close(1)
    os.open(logfile, os.O_WRONLY)

    # render the image
    bpy.ops.render.render(write_still=True)

    # disable output redirection
    os.close(1)
    os.dup(old)
    os.close(old)


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
        return False

# The following functions are used to check if objects are within the camera's view range
# code from https://blender.stackexchange.com/questions/45146/how-to-find-all-objects-in-the-cameras-view-with-python


def camera_as_planes(scene, obj):
    """
    Return planes in world-space which represent the camera view bounds.
    """

    camera = obj.data
    # normalize to ignore camera scale
    matrix = obj.matrix_world.normalized()
    frame = [matrix @ v for v in camera.view_frame(scene=scene)]
    origin = matrix.to_translation()

    planes = []
    is_persp = (camera.type != 'ORTHO')
    for i in range(4):
        # find the 3rd point to define the planes direction
        if is_persp:
            frame_other = origin
        else:
            frame_other = frame[i] + matrix.col[2].xyz

        n = normal(frame_other, frame[i - 1], frame[i])
        d = -n.dot(frame_other)
        planes.append((n, d))

    if not is_persp:
        # add a 5th plane to ignore objects behind the view
        n = normal(frame[0], frame[1], frame[2])
        d = -n.dot(origin)
        planes.append((n, d))

    return planes


def side_of_plane(p, v):
    return p[0].dot(v) + p[1]


def is_segment_in_planes(p1, p2, planes):
    dp = p2 - p1

    p1_fac = 0.0
    p2_fac = 1.0

    for p in planes:
        div = dp.dot(p[0])
        if div != 0.0:
            t = -side_of_plane(p, p1)
            if div > 0.0:
                # clip p1 lower bounds
                if t >= div:
                    return False
                if t > 0.0:
                    fac = (t / div)
                    p1_fac = max(fac, p1_fac)
                    if p1_fac > p2_fac:
                        return False
            elif div < 0.0:
                # clip p2 upper bounds
                if t > 0.0:
                    return False
                if t > div:
                    fac = (t / div)
                    p2_fac = min(fac, p2_fac)
                    if p1_fac > p2_fac:
                        return False

    # If we want the points
    # p1_clip = p1.lerp(p2, p1_fac)
    # p2_clip = p1.lerp(p2, p2_fac)
    return True


def point_in_object(obj, pt):
    xs = [v[0] for v in obj.bound_box]
    ys = [v[1] for v in obj.bound_box]
    zs = [v[2] for v in obj.bound_box]
    pt = obj.matrix_world.inverted() @ pt
    return (min(xs) <= pt.x <= max(xs) and
            min(ys) <= pt.y <= max(ys) and
            min(zs) <= pt.z <= max(zs))


def is_object_in_planes(obj, planes):

    matrix = obj.matrix_world
    box = [matrix @ Vector(v) for v in obj.bound_box]
    for v in box:
        if all(side_of_plane(p, v) > 0.0 for p in planes):
            # one point was in all planes
            return True

    # possible one of our edges intersects
    edges = ((0, 1), (0, 3), (0, 4), (1, 2),
             (1, 5), (2, 3), (2, 6), (3, 7),
             (4, 5), (4, 7), (5, 6), (6, 7))
    if any(is_segment_in_planes(box[e[0]], box[e[1]], planes)
           for e in edges):
        return True
    return False


def is_object_in_camera(camera, object_name):
    scene = context.scene
    origin = camera.matrix_world.to_translation()
    planes = camera_as_planes(scene, camera)
    object = get_object(object_name)
    return point_in_object(object, origin) or is_object_in_planes(object, planes)

# materail operations


def create_RGB_material(name, RGB="black"):
    mat = bpy.data.materials.get(name)

    if mat is None:
        mat = bpy.data.materials.new(name=name)

    mat.use_nodes = True
    if mat.node_tree:
        mat.node_tree.links.clear()
        mat.node_tree.nodes.clear()

    node_output = mat.node_tree.nodes.new(type="ShaderNodeOutputMaterial")
    node_input = mat.node_tree.nodes.new(type="ShaderNodeRGB")
    mat.node_tree.links.new(node_output.inputs[0], node_input.outputs[0])

    if RGB == "white":
        RGB = (1, 1, 1, 1)
    elif RGB == "black":
        RGB = (0, 0, 0, 1)

    mat.node_tree.nodes.get('RGB').outputs[0].default_value = RGB

    return mat


def set_background_color(RGB="black"):

    if RGB == "white":
        RGB = (1, 1, 1, 1)
    elif RGB == "black":
        RGB = (0, 0, 0, 1)

    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = RGB


def clear_set_material(object, materail):
    if object.type != "MESH":
        return
    object.select_set(True)
    bpy.context.view_layer.objects.active = object
    object.data.materials.clear()
    object.data.materials.append(materail)
    bpy.ops.object.select_all(action='DESELECT')
