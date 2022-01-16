from re import I
from typing import Dict, List
import numpy as np
import cv2
from pprint import pprint, pformat
from pathlib import Path
import random
import shutil
from tqdm import tqdm

def bbox(mask: np.ndarray):
    """generate a bounding box
    
    input: binary mask image array
    return: (x_min, y_min, x_max, y_max)
    """
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    
    return tuple([v.item() for v in (cmin, rmin, cmax, rmax)])

def binary_mask(img: np.ndarray):
    """generate a cleaner mask with binary color (black and white only)

    Args:
        img (np.ndarray): [original greyed mask]
    return: a cleaner mask with binary color
    """
    img_float = (img.astype('float32')) / 127 # threshold for binary color
    mask = np.dot(img_float[..., :3], [1/3, 1/3, 1/3]).astype('uint8')
    return mask

def generate_mask_and_bbox(param: Dict, dataset_dir: str):
    dataset_path = Path(dataset_dir)
    img = cv2.imread(str(dataset_path / "masks" / f"img_{param['id']}.png"))
    
    mask = binary_mask(img)
    box = bbox(mask)
    
    # save mask to npy file (faster to read/write)
    mask_file_name = str(f"mask_{param['id']}.npy")
    np.save(str(dataset_path / "masks" / mask_file_name), mask)
    
    # update dataset configs
    param['bbox'] = box
    param['mask'] = mask_file_name
    param['dimension'] = list(img.shape)
        

if __name__ == '__main__':
    test_mask = Path("generated/masks",
                     "img_b91cd0522cef43ddb32ba1ac6c45be23.png")

    im = cv2.imread(str(test_mask))

    print(list(im.shape), im.dtype, type(im))
    mask = binary_mask(im)
    box = bbox(mask)
    print(box, type(box[0]))
    cv2.rectangle(im, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 1)
    
    cv2.imshow("masks", im)

    cv2.waitKey(0)
