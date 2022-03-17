from typing import Optional
import sys
import subprocess
import os
from pathlib import Path


class PixelartExccuter(object):
    def __init__(
        self,
        blender_dir: Optional[str] = None,
        script: Optional[str] = None,
        blend: Optional[str] = None,
        background: bool = True,
    ):
        """
        input:
            blender_dir:    directory of blender executable (optional for Linux)
            script:         path to blender script (optional)
            blend:          path to blend file (optional)
            background:     bool to run background or with UI (default: True)
        """
        self._blender = "./blender"
        if sys.platform == "win32":
            self._blender = "blender.exe"
        elif sys.platform == "darwin":
            self._blender = "./blender"
        self._blender_dir = blender_dir
        self._script = script
        self._blend = blend
        self._background = background

    def run(self):
        command = [self._blender]
        if self._blend:
            command.extend([self._blend])
        if self._background:
            command.extend(["-b"])
        if self._script:
            command.extend(["--python", self._script])
        print(f"Executing command {' '.join(command)}")
        self._process = subprocess.Popen(
            ' '.join(command),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self._blender_dir,
        )

        return self._process

    def wait(self, output_path = None):
        out = open(output_path, 'w') if output_path else sys.stdout
        err = open(output_path, 'w') if output_path else sys.stderr
        for line in iter(self._process.stdout.readline, b""):
            print(line.decode("utf-8"), end="", file=out)
        for line in iter(self._process.stderr.readline, b""):
            print(line.decode("utf-8"), end="", file=err)
        self._process.wait()
