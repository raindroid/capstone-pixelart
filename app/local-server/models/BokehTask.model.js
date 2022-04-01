const mongoose = require("mongoose");

const { Schema } = mongoose;
const BokehTaskSchema = new Schema(
  {
    image: {
      type: String,
      required: true,
    },
    taskFinished: {
      type: Boolean,
      required: true,
      default: false,
    },
    type: {
      modelName: String,
      iterations: Number,
    }, // includes info like AI model name or iterations
    size: {
      width: Number,
      height: Number,
    },
  },
  { collection: "bokehs" }
);

const BokehTask = mongoose.model("BokehTask", BokehTaskSchema);

module.exports = BokehTask;
