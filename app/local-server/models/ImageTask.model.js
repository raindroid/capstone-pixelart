const mongoose = require("mongoose");
const BokehTask = require("./BokehTask.model");

const { Schema } = mongoose;
const ImageTaskSchema = new Schema(
  {
    image: { type: String, required: true },
    sizeLimit: Number,
    size: {
      width: Number,
      height: Number,
    },
    taskState: String,
    taskFinished: {
      type: Boolean,
      required: true,
      default: false,
    },
    imageMaskExists: Boolean,
    imageMasksReady: Boolean,
    imageMasks: [
      {
        image: { type: Schema.Types.ObjectId, ref: "Image" },
        confidence: Number,
        bbox: [Number],
        imageBokeh: [{ type: Schema.Types.ObjectId, ref: "BokehTask" }],
      },
    ],
    imageDepthReady: Boolean,
    imageDepth: {
      image: { type: Schema.Types.ObjectId, ref: "Image" },
      imageBokeh: [{ type: Schema.Types.ObjectId, ref: "BokehTask" }],
    },
  },
  { collection: "images" }
);

const ImageTask = mongoose.model("ImageTask", ImageTaskSchema);

module.exports = ImageTask;
