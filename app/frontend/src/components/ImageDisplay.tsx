import React, { useState } from "react";
import { makeStyles } from "@material-ui/core/styles";
import {
  Theme,
  Button,
  useMediaQuery,
  useTheme,
  IconButton,
  Modal,
  Paper,
} from "@material-ui/core";
import { AiOutlineRotateLeft, AiOutlineRotateRight } from "react-icons/ai";

import { MdCancel, MdCompare } from "react-icons/md";

import ReactCompareImage from "react-compare-image";
import { TransformWrapper, TransformComponent } from "react-zoom-pan-pinch";

// import Lightbox from "react-image-lightbox";
import Lightbox from "../git/react-image-lightbox/src";
import "react-image-lightbox/style.css"; // This only needs to be imported once in your app

const useStyles = makeStyles((theme: Theme, props?: any) => ({
  root: {
    position: "initial",
    width: "100%",
    height: "100%",
    zIndex: 10,
  },
  buttonImage: {
    color: "lightgrey",
  },
  comparePaper: {
    display: "flex",
    flexDirection: "column",
    width: "100%",
    height: "100%",
    alignItems: "center",
    justifyContent: "center",
    background: "rgba(241,241,241,0.1)",
    "&>div:nth-child(2)": {
      width: "96% !important",
      height: "96% !important",
      "& img": {
        objectFit: "scale-down !important",
      },
    },
  },
}));

export default function ImageDisplay(props: {
  selectedImage: any | null;
  originalImage: any | null;
  setShowImage: Function;
  nextImage?: string;
  prevImage?: string;
  moveNextImage?: () => void;
  movePrevImage?: () => void;
}) {
  const classes = useStyles(props);
  const {
    originalImage,
    setShowImage,
    selectedImage,
    moveNextImage,
    movePrevImage,
    nextImage,
    prevImage,
  } = props;

  const theme = useTheme();
  const matches = useMediaQuery(theme.breakpoints.up("sm")); // Variable for media query

  const [rotate, setRotate] = useState(0);

  const rotateButtons = [
    <IconButton onClick={() => setRotate((r) => r - 90)}>
      <AiOutlineRotateLeft className={classes.buttonImage} />
    </IconButton>,
    <IconButton onClick={() => setRotate((r) => r + 90)}>
      <AiOutlineRotateRight className={classes.buttonImage} />
    </IconButton>,
  ];

  const [openCompare, setOpenCompare] = useState(false);

  const compareButton = (
    <IconButton onClick={() => setOpenCompare(true)}>
      <MdCompare className={classes.buttonImage} />
    </IconButton>
  );

  return (
    <div className={classes.root}>
      <Modal open={openCompare} onClose={() => setOpenCompare(false)}>
        <Paper className={classes.comparePaper}>
          <div>
            <IconButton onClick={() => setOpenCompare(false)}>
              <MdCancel className={classes.buttonImage} />
            </IconButton>
          </div>
          {originalImage && (
            <ReactCompareImage
              leftImage={originalImage}
              rightImage={selectedImage}
            />
          )}
        </Paper>
      </Modal>
      <Lightbox
        mainSrc={selectedImage}
        onCloseRequest={() => setShowImage(false)}
        nextSrc={nextImage}
        prevSrc={prevImage}
        imagePadding={matches ? 160 : 20}
        onMoveNextRequest={moveNextImage}
        onMovePrevRequest={movePrevImage}
        toolbarButtons={[compareButton, ...rotateButtons]}
        reactModalStyle={{
          overlay: { zIndex: 1200 },
          content: {},
          image: { rotate: rotate },
          ".ril__toolbar": { top: 0 },
        }}
      />
    </div>
  );
}
