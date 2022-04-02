from pathlib import Path
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import traceback
import timeit

from libpixelartbokeh.ObjectDetection import ObejctDetection
from libpixelartbokeh.MegaDepthMap import MegaDepthMap
from libpixelartbokeh.PyNet import PyNet

global models
models = None

def initModels(pynet_checkpoint="best.ckpt"):
    global models
    if models is not None: 
        del models
    home = Path(__file__).parent.resolve()
    objectDetectioModel = ObejctDetection(checkpoint_path=str(home / "pretrain/pretrain_maskrcnn.pt"))
    megaDepthMapModel = MegaDepthMap(checkpoint_path=str(home / "pretrain/depthmap.pth"))
    pyNet = PyNet(checkpoint_path=str(home / "pretrain/PyNET" / pynet_checkpoint))
    models = (objectDetectioModel, megaDepthMapModel, pyNet)

initModels()

def getMasks(img):
    s_time = timeit.default_timer()
    # mask generation
    mask, confidence = None, None
    try:
        mask, confidence = models[0].predict(img)
        print(f"Gnerated mask shape {mask.shape}", end="\t")
    except Exception as e:
        print(e)
        traceback.print_exc()
    print(f"Time spent: {timeit.default_timer() - s_time:7.3f}s")
    return mask, confidence

def getDepthMap(img):
    s_time = timeit.default_timer()
    # depth generation
    depthmap = None
    try:
        depthmap = models[1].predict(img)
        print(f"Gnerated depth map shape {depthmap.shape}", end="\t")
    except Exception as e:
        print(e)
        traceback.print_exc()
    print(f"Time spent: {timeit.default_timer() - s_time:7.3f}s")
    return depthmap

def getBokehImage(img, mask):
    s_time = timeit.default_timer()
    # bokeh/blur generation
    bokeh_img = None
    try:
        bokeh_img = models[2].predict(img, mask=mask)[-1]
        print(f"Gnerated bokeh image shape {bokeh_img.shape}", end="\t")
    except Exception as e:
        print(e)
        traceback.print_exc()
    print(f"Time spent: {timeit.default_timer() - s_time:7.3f}s")
    return bokeh_img

if __name__ == "__main__":
    initModels()

    samples_path = Path("./res/samples")
    results_path = Path("./res/results")
    mask_results = []
    depth_results = []
    bokeh_results = []

    for sample in samples_path.iterdir():
        if sample.is_file():
            # Load image
            s_time = timeit.default_timer()
            try:
                img = Image.open(sample).convert("RGB")
                ratio = np.min((1920 / img.size[0], 1920 / img.size[1]))
                new_shape = np.array((img.size[0] * ratio, img.size[1] * ratio)).astype(np.uint32)
                img = img.resize(new_shape, Image.ANTIALIAS) 
                img = np.array(img)
                print(f"Loaded image {str(sample)} with shape {img.size} new_shape {img.shape}", end="\t")
            except Exception as e:
                print(e)
                traceback.print_exc()
            print(f"Time spent: {timeit.default_timer() - s_time:7.3f}s")
            
            
            mask_results = getMasks(img)
            imageMasks = []
            for mask, confidence in zip(*mask_results):
                print(f"Confi: {confidence}")
                bokeh = getBokehImage(img, mask=mask[0])

            depth = getDepthMap(img)
            bokeh = getBokehImage(img, mask=depth)
        
            
            Image.fromarray((bokeh * 255.).astype(np.uint8)).save(f"./res/results/{sample.stem}_bokeh.png")
            break
