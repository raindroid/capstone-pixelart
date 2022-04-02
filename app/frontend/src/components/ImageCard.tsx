import React, { useEffect, useState } from "react";
import { makeStyles } from "@material-ui/core/styles";
import {
  IconButton,
  Theme,
  Button,
  Card,
  CardContent,
  CardActions,
  LinearProgress,
  ButtonGroup,
} from "@material-ui/core";
import Typography from "@material-ui/core/Typography";
import ImageDisplay from "./ImageDisplay";
import { HorizontalSplit } from "@material-ui/icons";

const useStyles = makeStyles((theme: Theme, props?: any) => ({
  root: {
    position: "relative",
    width: "100%",
    paddingTop: 12,
    maxHeight: "calc(100% - 80px)",
  },

  cardRoot: {
    position: "relative",
    width: "fit-content",
    height: "fit-content",
    margin: "0 auto",
    "& .MuiCardContent-root": {
      paddingBottom: 2,
    }
  },

  imgPreview: {
    maxWidth: 800,
    maxHeight: 480,

    [theme.breakpoints.down("sm")]: {
      maxWidth: 560,
      maxHeight: 360,
    },
    [theme.breakpoints.down("xs")]: {
      maxWidth: 320,
      maxHeight: 360,
    },
  },
  stateTypo: {
    fontSize: "0.85rem",
  },
  resButtonGroupParentHorizontal: {
    display: "flex",
    flexDirection: "row",
    alignContent: "center",
    justifyContent: "center",
    alignItems: "center",
    margin: "0 auto",
  },
  resButtonGroupParentDepth: {
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "flex-end",
    margin: "0 auto",
  },
  resButtonGroupParentMask: {
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "flex-start",
    margin: "0 auto",
  },
  resButtonGroup: {
    margin: "0 auto",
  },
  button: {
    padding: 2,
    margin: 0
  }
}));

export default function ImageCard(props: {
  selectedImage: any | null;
  taskData?: any;
  maskData?: any;
  loading?: boolean | null;
}) {
  const classes = useStyles(props);
  const { taskData, maskData } = props;
  const [showImage, setShowImage] = useState<any | null>(null);
  const [masks, setMasks] = useState<string[]>([]);
  const [blurs, setBlurs] = useState<string[]>([]);
  const [imageOpened, setImageOpened] = useState<{
    type: "mask" | "blur";
    index: number;
    nextImage: number | null;
    prevImage: number | null;
  } | null>(null);
  let { selectedImage } = props;

  const convertB64toImage = (b64: string) => `data:image/jpeg;base64,${b64}`;
  useEffect(() => {
    if (taskData?.getTask && maskData?.getTask) {
      const newMasks = [
        convertB64toImage(maskData?.getTask?.imageDepth?.image?.content),
      ].concat(
        maskData.getTask?.imageMasks?.map((mask?: any) =>
          convertB64toImage(mask?.image?.content)
        )
      );
      const newBlurs = [
        convertB64toImage(
          maskData?.getTask?.imageDepth?.imageBokeh[0]?.image?.content
        ),
      ].concat(
        maskData.getTask?.imageMasks?.map((mask?: any) =>
          convertB64toImage(mask?.imageBokeh[0]?.image?.content)
        )
      );
      setMasks(newMasks);
      setBlurs(newBlurs);
      setImageOpened(null);
    }
  }, [
    maskData?.getTask,
    maskData?.getTask?.imageDepth?.image,
    maskData?.getTask?.imageDepth?.imageBokeh,
    maskData?.getTask.imageMask,
    maskData?.getTask?.imageMasks,
    maskData?.getTask.taskFinished,
    taskData,
  ]);

  if (typeof selectedImage !== "string") {
    selectedImage = URL.createObjectURL(selectedImage);
  }

  // Progress updates
  const stateMsg = taskData?.getTask?.taskState || "Not found";
  let progress: number = 0;
  if (stateMsg.includes("queue")) progress = 10;
  if (stateMsg.includes("loaded original")) progress = 20;
  if (stateMsg.includes("found")) progress = 30;
  if (stateMsg.includes("generated mask")) progress = 60;
  if (stateMsg.includes("generated depth map")) progress = 80;
  if (stateMsg.includes("all done")) progress = 100;
  if (stateMsg.includes("Not found")) progress = 0;
  if (maskData?.getTask.taskFinished) progress = 100;
  // console.log(maskData);

  useEffect(() => {
    setImageOpened(null);
  }, [selectedImage]);

  const loadMaskImage = (index: number) => {
    setImageOpened({
      type: "mask",
      index: index,
      prevImage: index > 0 ? index - 1 : null,
      nextImage: index < masks.length - 1 ? index + 1 : null,
    });
    setShowImage(masks[index]);
  };
  const loadBlurImage = (index: number) => {
    setImageOpened({
      type: "blur",
      index: index,
      prevImage: index > 0 ? index - 1 : null,
      nextImage: index < blurs.length - 1 ? index + 1 : null,
    });
    setShowImage(blurs[index]);
  };
  const moveNextImage = () => {
    if (imageOpened) {
      const { type, index } = imageOpened;
      if (type === "mask" && index < masks.length - 1) {
        loadMaskImage(index + 1);
      } else if (type === "blur" && index < blurs.length - 1) {
        loadBlurImage(index + 1);
      }
    }
  };
  const movePrevImage = () => {
    if (imageOpened) {
      const { type, index } = imageOpened;
      if (type === "mask" && index > 0) loadMaskImage(index - 1);
      else if (type === "blur" && index > 0) loadBlurImage(index - 1);
    }
  };

  return (
    <div className={classes.root}>
      <Card className={classes.cardRoot}>
        <CardContent>
          <img
            className={classes.imgPreview}
            src={selectedImage}
            alt="preivew"
            onClick={() => setShowImage(selectedImage)}
          />
          {showImage && (
            <ImageDisplay
              setShowImage={setShowImage}
              selectedImage={showImage}
              moveNextImage={moveNextImage}
              movePrevImage={movePrevImage}
              nextImage={
                imageOpened?.nextImage
                  ? imageOpened.type === "mask"
                    ? masks[imageOpened.nextImage]
                    : blurs[imageOpened.nextImage]
                  : undefined
              }
              prevImage={
                imageOpened && imageOpened.prevImage !== null
                  ? imageOpened.type === "mask"
                    ? masks[imageOpened.prevImage]
                    : blurs[imageOpened.prevImage]
                  : undefined
              }
            />
          )}
          {selectedImage && (
            <LinearProgress
              variant="determinate"
              value={progress}
              color="secondary"
            />
          )}
          {selectedImage && (
            <Typography variant="h6" className={classes.stateTypo}>
              Processing state: {stateMsg}
            </Typography>
          )}
        </CardContent>
        <CardActions>
          {selectedImage && progress === 100 && (
            <div className={classes.resButtonGroupParentHorizontal}>
              <div className={classes.resButtonGroupParentDepth}>
                <Button
                  color="secondary"
                  variant="contained"
                  className={classes.button}
                  onClick={() => loadMaskImage(0)}
                >
                  Depth
                </Button>
                <Button
                  color="primary"
                  variant="outlined"
                  className={classes.button}
                  onClick={() => loadBlurImage(0)}
                >
                  Blur 0
                </Button>
              </div>
              <div className={classes.resButtonGroupParentMask}>
                <ButtonGroup
                  color="secondary"
                  variant="contained"
                  aria-label="Show Results"
                  className={classes.resButtonGroup}
                >
                  {maskData?.getTask?.imageMasks?.map(
                    (mask: any, index: number) => (
                      <Button
                      className={classes.button}
                        onClick={() => loadMaskImage(index + 1)}
                        key={index + 1}
                      >
                        Mask {index + 1}
                      </Button>
                    )
                  )}
                </ButtonGroup>
                <ButtonGroup
                  color="primary"
                  aria-label="Show Results"
                  className={classes.resButtonGroup}
                >
                  {maskData?.getTask?.imageMasks?.map(
                    (mask: any, index: number) => (
                      <Button
                      className={classes.button}
                        onClick={() => loadBlurImage(index + 1)}
                        key={index + 1}
                      >
                        Blur {index + 1}
                      </Button>
                    )
                  )}
                </ButtonGroup>
              </div>
            </div>
          )}
        </CardActions>
      </Card>
    </div>
  );
}
