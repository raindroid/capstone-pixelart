import React, { useState } from "react";
import { makeStyles } from "@material-ui/core/styles";
import {
  IconButton,
  Theme,
  Button,
  useMediaQuery,
  useTheme,
} from "@material-ui/core";

import Lightbox from "react-image-lightbox";
import "react-image-lightbox/style.css"; // This only needs to be imported once in your app

const useStyles = makeStyles((theme: Theme, props?: any) => ({
  root: {
    position: "initial",
    width: "100%",
    height: "100%",
    zIndex: 10,
  },
}));

export default function ImageDisplay(props: {
  selectedImage: any | null;
  setShowImage: Function;
  nextImage?: string;
  prevImage?: string;
  moveNextImage?: () => void;
  movePrevImage?: () => void;
}) {
  const classes = useStyles(props);
  const {
    setShowImage,
    selectedImage,
    moveNextImage,
    movePrevImage,
    nextImage,
    prevImage,
  } = props;

  const theme = useTheme();
  const matches = useMediaQuery(theme.breakpoints.up("sm")); // Variable for media query

  return (
    <div className={classes.root}>
      <Lightbox
        mainSrc={selectedImage}
        onCloseRequest={() => setShowImage(false)}
        nextSrc={nextImage}
        prevSrc={prevImage}
        imagePadding={matches ? 160 : 20}
        onMoveNextRequest={moveNextImage}
        onMovePrevRequest={movePrevImage}
        reactModalStyle={{ ".ril__toolbar": { top: 100 } }}
      />
    </div>
  );
}
