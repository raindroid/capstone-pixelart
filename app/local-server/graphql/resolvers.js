const sanitize = require("mongo-sanitize");
const { default: mongoose } = require("mongoose");
const ImageTask = require("../models/ImageTask.model");
const crypto = require("crypto");
const http = require("http");
const BokehTask = require("../models/BokehTask.model");

require("dotenv").config();

const callPython = async () => {
  // ask the python backedn to continue working!
  const python_port = process.env.BACKEND_PYTHON_PORT || 5000;
  await http
    .get(`http://localhost:${python_port}/wake`, (res) =>
      console.log(`Woke up python -- Status: ${res.statusCode}`)
    )
    .on("error", () => {
      console.log("Error when waking up python");
      return "Connection Error";
    });
  return "Done";
};

const resolvers = {
  Query: {
    hello: () => {
      return "Hello world";
    },
    getAllTasks: async () => {
      return await ImageTask.find();
    },
    getTask: async (_, { id }) => {
      callPython(); // in case the python missed the task before
      id = sanitize(id);
      return await ImageTask.findById(id);
    },
    getBokeh: async (_, { id }) => {
      id = sanitize(id);
      return await BokehTask.findById(id);
    },
    wakePython: () => {
      return callPython();
    },
  },
  ImageMask: {
    imageBokeh: async ({ imageBokeh }, args) =>
      await imageBokeh.map((id) => {
        return BokehTask.findById(id);
      }),
  },
  ImageDepth: {
    imageBokeh: async ({ imageBokeh }, args) =>
      await imageBokeh.map((id) => {
        return BokehTask.findById(id);
      }),
  },
  Mutation: {
    sendImageRequest: async (_, { image, sizeLimit }) => {
      sizeLimit = sizeLimit || 1920
      // check for duplicates
      const preRes = await ImageTask.find({ image, sizeLimit });

      if (preRes && preRes.length > 0) {
        const taskId = preRes[0]._id;
        console.log(
          `[saveImageTask] Found duplicate copies for imageTask ${taskId}, res is ${
            preRes && preRes.length
          }`
        );
        return taskId;
      } else {
        const imageTaskEntry = new ImageTask({
          image,
          sizeLimit,
          taskState: "init",
        });
        const res = await imageTaskEntry.save();

        const taskId = res._id;
        console.log(`[saveImageTask] Saved new imageTask, res id is ${taskId}`);

        // Log purpose
        const allRes = await ImageTask.find();
        console.log(
          `[saveImageTask] Currently saved ${
            allRes ? allRes.length : 0
          } imageTasks`
        );

        // wake up backend python
        callPython();

        return taskId;
      }
    },
  },
};

module.exports = resolvers;
