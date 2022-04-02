import asyncio
from datetime import date, datetime
from queue import Queue
from threading import Thread
from time import sleep
import traceback
from flask import Flask, request
import json, os
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
import base64
import io
import numpy as np
import gc

from mongodb import (
    insertBokehTask,
    insertImage,
    startTask,
    unfinishedTasks,
    updateImageTask,
)
from test import initModels, getBokehImage, getDepthMap, getMasks

home = Path(__file__).parent.resolve().parent.resolve()
pynet_ckpt = os.environ.get("PYNET_CHECKPOINT", "best.ckpt")
initModels(str(home / "backend/pretrain/PyNET" / pynet_ckpt))

load_dotenv(str(home / "local-server/.env"))

app = Flask(__name__)

taskQ = Queue()
taskCounter = 0
image_limit = 1920  # 1920


def printTime():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)


def encodeImageBase64(img):
    buffered = io.BytesIO()
    if np.max(img) <= 1.0:
        img = (img * 255).astype(np.uint8)
    im = Image.fromarray(img)
    if im.mode != "RGB":
        im = im.convert("RGB")
    im.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("ascii")


def bbox(img):
    a = np.where(img > 0.45)
    bbox = (
        int(np.min(a[1])),
        int(np.max(a[1])),
        int(np.min(a[0])),
        int(np.max(a[0])),
    )
    return bbox


def worker(task):
    gc.collect()
    id = task["_id"]
    img_base64 = task["image"]
    size_limit = task["sizeLimit"]
    if size_limit is None or size_limit > image_limit:
        size_limit = image_limit
    size_limit = int(size_limit * 0.8)

    base64_decoded = base64.b64decode(img_base64)
    img = Image.open(io.BytesIO(base64_decoded))

    ratio = np.min(
        (size_limit / img.size[0], size_limit / img.size[1], 1)
    )
    new_shape = np.array((img.size[0] * ratio, img.size[1] * ratio)).astype(
        np.uint32
    )
    img = img.resize(new_shape, Image.ANTIALIAS)
    img = np.array(img)
    if img is not None and np.max(img) > 1:
        img = img.astype(np.float32) / 255.0
    print(f"WORKER: Loaded image {id} with shape {img.shape} (sizeLimit: {size_limit}, ratio: {ratio})")
    ## update stat info
    updateImageTask(
        {
            "_id": id,
            "taskState": "loaded original image...",
            "size.width": int(img.shape[1]),
            "size.height": int(img.shape[0]),
        }
    )

    mask_results = getMasks(img)
    imageMasks = []

    mask_exists = mask_results[0] is not None and len(mask_results[0]) > 0
    if mask_exists:
        masks = []
        for i, (mask, confidence) in enumerate(zip(*mask_results)):
            if confidence > 0.4:
                masks.append((mask, confidence))
        mask_exists = len(masks) > 0

        print(f"WORKER: Found {len(masks)} masks")
        updateImageTask(
            {
                "_id": id,
                "taskState": f"found {len(masks)} mask(s)...",
            }
        )
        for i, (mask, confidence) in enumerate(masks):
            mask = mask[0]
            if mask is not None and np.max(mask) > 1:
                mask = mask.astype(np.float32) / 255.0
            print(f"WORKER: Confi: {confidence}")
            bokeh = getBokehImage(img, mask=mask)
            print(f"Mask shape {mask.shape}")
            mask_id = insertImage(encodeImageBase64(mask), mask.shape)
            imageMasks.append(
                {
                    "image": mask_id,
                    "confidence": float(confidence),
                    "bbox": bbox(mask),
                    "imageBokeh": [
                        insertBokehTask(
                            encodeImageBase64(bokeh),
                            pynet_ckpt,
                            1,
                            shape=bokeh.shape,
                        )
                    ],
                }
            )
            updateImageTask(
                {
                    "_id": id,
                    "imageMaskExists": mask_exists,
                    "imageMasksReady": True,
                    "imageMasks": imageMasks,
                    "taskState": f"generated mask bokeh ({i+1} / {len(mask_results[0])}...",
                }
            )

    depth = getDepthMap(img)
    depth_id = insertImage(encodeImageBase64(depth), depth.shape)
    updateImageTask(
        {
            "_id": id,
            "imageDepth": {"image": depth_id},
            "taskState": f"generated depth map...",
        }
    )
    bokeh = getBokehImage(img, mask=depth)
    imageDepth = {
        "image": depth_id,
        "imageBokeh": [
            insertBokehTask(
                encodeImageBase64(bokeh), pynet_ckpt, 1, shape=bokeh.shape
            )
        ],
    }

    updateImageTask(
        {
            "_id": id,
            "imageDepthReady": True,
            "imageDepth": imageDepth,
            "taskFinished": True,
            "taskState": "all done!",
        }
    )
    print(f"WORKER: Finished image {id} with shape {bokeh.shape}")
    return True


def WorkderManager():
    while True:
        print("WorkerManager: Waiting for tasks")
        try:
            task = taskQ.get(True)
            id = task.get("_id", None)
            # check for consistency
            if id is not None:
                # someone said mongod has a per `mongod` read/write lock!
                # https://stackoverflow.com/questions/17456671/to-what-level-does-mongodb-lock-on-writes-or-what-does-it-mean-by-per-connec
                task = startTask(task)
                if task is not None and task is not False:
                    print(f"Got task with id - {id}")
                    printTime()
                    if worker(task):
                        print(f"Successfully done the task - {id}")
                    else:
                        print(f"Failed task - {id}")
        except Exception as e:
            print(e)
            traceback.print_exc()
            updateImageTask({"_id": id, "taskState": f"ERROR: {e}"})


@app.route("/wake", methods=["GET", "POST"])
def execute():
    # read data from mongoose
    # check all unfinished requests
    print("I'm actively checking all tasks")
    # send task
    [taskQ.put(task) for task in unfinishedTasks()]

    return {"status": "perfect"}


WorkerManagerThread = Thread(target=WorkderManager)
WorkerManagerThread.start()

if __name__ == "__main__":
    # port selection will not work with flusk run
    port = int(os.environ.get("BACKEND_PYTHON_PORT", "5000"))
    app.run(port=port)
