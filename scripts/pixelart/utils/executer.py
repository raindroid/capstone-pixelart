from typing import Optional
import sys, subprocess, os
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
        self._blender = "blender.exe" if os.name == "nt" else "blender"
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
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self._blender_dir,
        )

        return self._process

    def wait(self):
        for line in iter(self._process.stdout.readline, b""):
            print(line.decode("utf-8"), end="")
        for line in iter(self._process.stderr.readline, b""):
            print(line.decode("utf-8"), end="")
        self._process.wait()


if __name__ == "__main__":
    # exe = PixelartExccuter(
    #     "C:\\Program Files\\Blender Foundation\\Blender 2.93",
    #     "M:\\ECE496\\PixelArt\\model\\beginner\\beginner.py",
    #     "M:\\ECE496\\PixelArt\\model\\beginner\\beginner.blend",
    # )

    blender_dir = "C:\\Program Files\\Blender Foundation\\Blender 2.93"
    pixelart_path = Path("M:\\ECE496\\PixelArt\\")
    script_templace_path = str(
        pixelart_path / "scripts/pixelart/blend/sample.py.template"
    )
    script_path = str(pixelart_path / "work/sample.py")

    # create new working directory
    (pixelart_path / "work").mkdir(parents=True, exist_ok=True)
    configs = {"replacement": {"pixelart_path": str(pixelart_path).replace('\\', '\\\\')}}

    with open(script_templace_path, "r") as tempfile, open(script_path, "w") as outfile:
        for line in tempfile:
            for replacement in configs["replacement"].items():
                key = f"_$${replacement[0]}"
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
