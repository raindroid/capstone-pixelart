const mongoose = require("mongoose");
const BokehTask = require("./BokehTask.model");

const {Schema} = mongoose;
const ImageSchema = new Schema(
  {
    content: {
      type: String,
      required: true,
    },
    size: {
      width: Number,
      height: Number
    },
  },
  { collection: "image" }
);

const Image = mongoose.model("Image", ImageSchema);

module.exports = Image;
