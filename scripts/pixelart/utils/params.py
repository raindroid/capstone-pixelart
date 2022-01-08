# handling read and write parameters to and from json file

from typing import Dict
from pathlib import Path
import json, sys
from pprint import pprint

class PixelartParam(object):
    def __init__(self, name: str="params"):
        self._name = name
        self._value = {}

    def read(self, path: str) -> Dict:
        param_file = Path(path)
        if param_file.is_dir():
            param_file = Path(param_file, self._name)
        
        if param_file.is_file():
            try:
                with open(param_file) as pfile:
                    self._value = json.load(pfile)
            except Exception as e:
                print(f"ERROR reading parameter file: {e}", file=sys.stderr)
                raise(e)
        else:
            print(f"ERROR reading parameter file: file {path} not found", file=sys.stderr)
            raise(FileNotFoundError)
        
        return self._value

    def write(self, path: str) -> bool:
        param_file = Path(path)
        if param_file.is_dir():
            param_file = Path(param_file, self._name)
        
        try:
            with open(param_file, "w") as pfile:
                json.dump(self._value, pfile) 
        except Exception as e:
            print(f"ERROR writing parameter file: {e}", file=sys.stderr)
            raise(e)
        return True
    
    def create_object(self, name: str, collection_name: str, value: Dict = {}) -> Dict:
        self._value[name] = value
        return self._value[name]

if __name__ == "__main__":
    param = PixelartParam()
    # param._value = {
    #     'man': {
    #         'collection': 'Man',
    #         'object': 'metarig',
    #         'fixed_params': {},
    #         'randomized_params': {
                
    #         }
    #     }
    # }
    # param.write("models\params.json")
    # param.read("models\params.json")
    param.create_object("man", {})['object'] = 'metarig'
    pprint(param._value)