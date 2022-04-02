import { gql } from "@apollo/client";

export const GQL_WAKE_PYTHON = gql`
  query {
    wakePython
  }
`;

export const GQL_UPLOAD_IMAGE = gql`
  mutation ($image: String!, $sizeLimit: Int) {
    sendImageRequest(image: $image, sizeLimit: $sizeLimit)
  }
`;
export const GQL_GET_ALL_IMAGES = gql`
  query {
    getAllTasks {
      id
    }
  }
`;

export const GQL_GET_IMAGE_STATE = gql`
  query ($getTaskId: ID!) {
    getTask(id: $getTaskId) {
      id
      taskState
      sizeLimit
      size {
        width
        height
      }
      taskFinished
      imageMaskExists
      imageMasksReady
      imageMasks {
        confidence
        bbox
        imageBokeh {
          id
          type {
            modelName
            iterations
          }
          taskFinished
        }
      }
      imageDepthReady
      imageDepth {
        imageBokeh {
          id
          taskFinished
          type {
            modelName
            iterations
          }
        }
      }
    }
  }
`;

export const GQL_GET_MASKS = gql`
  query ($getTaskId: ID!) {
    getTask(id: $getTaskId) {
      id
      taskState
      taskFinished
      imageMaskExists
      imageMasksReady
      imageMasks {
        image
        size {
          width
          height
        }
        confidence
        imageBokeh {
          id
          image
        }
      }
      imageDepthReady
      imageDepth {
        image
        size {
          width
          height
        }
        imageBokeh {
          id
          image
        }
      }
    }
  }
`;

export const GQL_GET_BOKEH_IMAGE = gql`
  query ($getBokehId: ID!) {
    getBokeh(id: $getBokehId) {
      id
      taskFinished
      type {
        modelName
        iterations
      }
    }
  }
`;
