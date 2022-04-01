const mongoose = require("mongoose");
const BokehTask = require("./BokehTask.model");

const {Schema} = mongoose;
const ImageTaskSchema = new Schema(
  {
    image: {
      type: String,
      required: true,
    },
    sizeLimit: Number,
    size: {
      width: Number,
      height: Number
    },
    taskState: String,
    taskFinished: {
      type: Boolean,
      required: true,
      default: false,
    },
    imageMaskExists: Boolean,
    imageMaskReady: Boolean,
    imageMasks: [
      {
        image: String,
        confidence: Number,
        imageBokeh: [{ type: Schema.Types.ObjectId, ref: "BokehTask" }],
        size: {
          width: Number,
          height: Number
        },
      },
    ],
    imageDepthReady: Boolean,
    imageDepth: {
      image: String,
      imageBokeh: [{ type: Schema.Types.ObjectId, ref: "BokehTask" }],
      size: {
        width: Number,
        height: Number
      },
    },
  },
  { collection: "images" }
);

const ImageTask = mongoose.model("ImageTask", ImageTaskSchema);

module.exports = ImageTask;
