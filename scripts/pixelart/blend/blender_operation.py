# This file contains wrapper functions of common blender functions

from typing import Optional
import bpy
import os
from pathlib import Path


class BlenderOp(object):
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

    def create_camera(name: str = "MainCamera", dataname: Optional[str] = None):
        camera = bpy.data.cameras.new(name=name if dataname == None else dataname)
        camera_obj = bpy.data.objects.new(name, camera)
        bpy.context.scene.collection.objects.link(camera_obj)

        return camera_obj
