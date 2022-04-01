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
    type ImageBokeh {
        id: ID!
        image: String
        taskFinished: Boolean
        type: BokehType
        size: SizeType
    }
    type ImageMask {
        image: String
        confidence: Float
        imageBokeh: [ImageBokeh]
        size: SizeType
    }
    type ImageDepth {
        image: String
        imageBokeh: [ImageBokeh]
        size: SizeType
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
