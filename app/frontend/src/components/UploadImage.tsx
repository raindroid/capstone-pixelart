import React, { useState } from "react";
import { makeStyles } from "@material-ui/core/styles";
import { IconButton, Theme, Button } from "@material-ui/core";
import PhotoCamera from "@material-ui/icons/PhotoCamera";
import { useLazyQuery, useMutation } from "@apollo/client";
import { GQL_UPLOAD_IMAGE } from "../graphql/pixelart";
import { getBase64 } from "./helper";

const useStyles = makeStyles((theme: Theme) => ({
  root: {
    "& > *": {
      margin: theme.spacing(1),
    },
    position: "fixed",
    bottom: "8vh",
    left: 0,
    right: 0,
    [theme.breakpoints.down("md")]: {
      bottom: "4vh",
    },
    [theme.breakpoints.down("xs")]: {
      bottom: "6vh",
    },
  },
  input: {
    display: "none",
  },
}));

export default function UploadImage(props: {
  selectedImage: any;
  setSelectedImage: Function;
  renderTaskId: string | null;
  setRenderTaskId: Function;
}) {
  const classes = useStyles(props);
  const { selectedImage, setSelectedImage, setRenderTaskId } = props;

  const [sendImageTask] = useMutation(GQL_UPLOAD_IMAGE, {
    fetchPolicy: "no-cache",
    onError: (e) => {
      console.log("error", `GQL_UPLOAD_IMAGE: ${JSON.stringify(e)}`);
      alert(`Failed to Upload! \n${JSON.stringify(e)}\n\n`);
    },
    onCompleted: (data) => {
      console.log(`Received data from upload image ${data.sendImageRequest}`);
      setRenderTaskId(data.sendImageRequest);
    },
  });

  const analyze = () => {
    getBase64(selectedImage)
      .then((result: any) => {
        const image = result.substring(result.indexOf(",") + 1 || 0) || "";
        sendImageTask({
          variables: {
            image,
            sizeLimit: 1920,
          },
        });
      })
      .catch((err) => {
        console.log(err);
      });
  };

  return (
    <div className={classes.root}>
      <input
        accept="image/*"
        className={classes.input}
        id="contained-button-file"
        multiple
        type="file"
        onChange={(event: React.ChangeEvent<any>) => {
          console.log(event.target.files[0]);
          setSelectedImage(event.target.files[0]);
        }}
      />
      <label htmlFor="contained-button-file">
        <Button variant="contained" color="secondary" component="span">
          Upload
        </Button>
      </label>
      <input
        type="file"
        accept="image/*"
        capture="environment"
        className={classes.input}
        id="icon-button-file"
        onChange={(event: React.ChangeEvent<any>) => {
          console.log(event.target.files[0]);
          setSelectedImage(event.target.files[0]);
        }}
      />
      <label htmlFor="icon-button-file">
        <IconButton
          color="secondary"
          aria-label="upload picture"
          component="span"
        >
          <PhotoCamera />
        </IconButton>
      </label>

      <Button
        variant="contained"
        color="primary"
        component="span"
        onClick={analyze}
      >
        Analyze
      </Button>
    </div>
  );
}
