from inspect import trace
import traceback
from typing import Dict
import pymongo
from bson.objectid import ObjectId


def unfinishedTasks():
    with pymongo.MongoClient("mongodb://localhost:27017/") as client:
        pixelartdb = client["pixelart"]
        imageTasks = pixelartdb["images"]
        tasks = list(
            imageTasks.find({"taskFinished": False, "taskState": "init"})
        )
    return tasks


def startTask(task):
    with pymongo.MongoClient("mongodb://localhost:27017/") as client:
        pixelartdb = client["pixelart"]
        imageTasks = pixelartdb["images"]

        try:
            task["taskState"] = "in queue"
            oldTask = imageTasks.find_one_and_update(
                {"_id": ObjectId(task["_id"])},
                {"$set": {"taskState": "in queue"}},
            )
            if (
                oldTask is not None
                and oldTask.get("taskState", None) == "init"
            ):
                return task
        except Exception as e:
            print(e)
            traceback.print_exc()
        return False


def insertImage(image: str, shape):
    with pymongo.MongoClient("mongodb://localhost:27017/") as client:
        pixelartdb = client["pixelart"]
        imageTable = pixelartdb["image"]
        res = None
        try:
            res = imageTable.insert_one(
                {
                    "content": image,
                    "size": {
                        "width": int(shape[1]),
                        "height": int(shape[0]),
                    },
                }
            )
        except Exception as e:
            print(e)
            traceback.print_exc()

        return res.inserted_id if res is not None else None


def insertBokehTask(bokeh_image: str, modelName: str, iterations: str, shape):
    image_id = insertImage(bokeh_image, shape)
    with pymongo.MongoClient("mongodb://localhost:27017/") as client:
        pixelartdb = client["pixelart"]
        bokehTable = pixelartdb["bokehs"]
        res = None
        try:
            res = bokehTable.insert_one(
                {
                    "image": image_id,
                    "type": {"modelName": modelName, "iterations": iterations},
                    "taskFinished": True,
                }
            )
        except Exception as e:
            print(e)
            traceback.print_exc()

        return res.inserted_id if res is not None else None


def updateImageTask(doc):
    with pymongo.MongoClient("mongodb://localhost:27017/") as client:
        pixelartdb = client["pixelart"]
        imageTasks = pixelartdb["images"]

        try:
            imageTasks.update_one({"_id": doc["_id"]}, {"$set": doc})
        except Exception as e:
            print(e)
            traceback.print_exc()
