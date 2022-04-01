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
            task['taskState'] = "in queue"
            oldTask = imageTasks.find_one_and_update(
                {"_id": ObjectId(task["_id"])},
                {"$set": task},
            )
            if oldTask.get("taskState", None) == "init":
                return task
        except Exception as e:
            print(e)
            traceback.print_exc()
        return False


def insertBokehTask(bokeh_image: str, modelName: str, iterations: str):
    with pymongo.MongoClient("mongodb://localhost:27017/") as client:
        pixelartdb = client["pixelart"]
        bokehTable = pixelartdb["bokehs"]
        res = None
        try:
            res = bokehTable.insert_one(
                {
                    "image": bokeh_image,
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
