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
export const GQL_GET_IMAGETASK_CONTENT = gql`
  query ($getTaskId: ID!) {
    getTask(id: $getTaskId) {
      id
      taskState
      sizeLimit
      image
      size {
        width
        height
      }
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
      imageMasks {
        confidence
      }
      taskFinished
      imageMaskExists
      imageMasksReady
      imageDepthReady
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
        image {
          id
          content
          size {
            width
            height
          }
        }
        confidence
        imageBokeh {
          id
          image {
            id
            content
            size {
              width
              height
            }
          }
        }
      }
      imageDepthReady
      imageDepth {
        image {
          id
          content
          size {
            width
            height
          }
        }
        imageBokeh {
          id
          image {
            id
            content
            size {
              width
              height
            }
          }
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
