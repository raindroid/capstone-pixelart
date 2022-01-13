# handling read and write parameters to and from json file

from typing import Dict, Optional
from pathlib import Path
import json, sys
from pprint import pprint

class PixelartParam(object):
    def __init__(self, path: Optional[str] = None, name: str="params"):
        self._name = name
        self._value = {}
        if path is not None:
            self.read(path)

    def read(self, path: str) -> Dict:
        param_file = Path(path)
        if param_file.is_dir():
            param_file = Path(param_file, self._name)
        
        try:
            with open(param_file) as pfile:
                self._value = json.load(pfile)

            self.generator = self._value['generator']
            self.camera = self._value['camera']
            self.objects = self._value['objects']
            self.scenes = self._value['scenes']
        except Exception as e:
            print(f"ERROR reading parameter file: {e}", file=sys.stderr)
            raise(e)

        return self._value

if __name__ == "__main__":
    param = PixelartParam("M:/ECE496/PixelArt/models/params.json")
    
    pprint(param.params.camera)