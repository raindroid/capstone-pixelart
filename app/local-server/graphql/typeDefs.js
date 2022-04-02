const { gql } = require("apollo-server-express");
const typeDefs = gql`
    type SizeType {
        width: Int
        height: Int
    }
    type BokehType {
        modelName: String
        iterations: Int
    }
    type ImageType {
        id: ID!
        content: String
        size: SizeType
    }
    type ImageBokeh {
        id: ID!
        image: ImageType
        taskFinished: Boolean
        type: BokehType
    }
    type ImageMask {
        image: ImageType
        confidence: Float
        bbox: [Int]
        imageBokeh: [ImageBokeh]
    }
    type ImageDepth {
        image: ImageType
        imageBokeh: [ImageBokeh]
    }
    type ImageTask {
        id: ID!
        image: String
        sizeLimit: Int
        size: SizeType
        taskState: String
        taskFinished: Boolean
        imageMaskExists: Boolean,
        imageMasksReady: Boolean
        imageMasks: [ImageMask]
        imageDepthReady: Boolean
        imageDepth: ImageDepth
    }
    type Mutation {
        sendImageRequest(image: String!, sizeLimit: Int): ID
    }
    type Query {
        hello: String
        wakePython: String
        getAllTasks: [ImageTask]
        getTask(id: ID!): ImageTask
        getBokeh(id: ID!): ImageBokeh
    }
`;

module.exports = typeDefs;
