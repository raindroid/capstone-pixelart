import React, { useEffect, useState } from "react";
import { makeStyles } from "@material-ui/core/styles";
import { IconButton, Theme, Button } from "@material-ui/core";
import PhotoCamera from "@material-ui/icons/PhotoCamera";
import ImageDisplay from "./ImageDisplay";
import ImageCard from "./ImageCard";
import { useQuery, useLazyQuery } from "@apollo/client";
import { GQL_GET_IMAGE_STATE, GQL_GET_MASKS } from "../graphql/pixelart";
import Typography from "@material-ui/core/Typography";
const bgUrl =
  "https://images.unsplash.com/photo-1574507355235-5042eb7af735?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1170&q=80";

const useStyles = makeStyles((theme: Theme, props?: any) => ({
  root: {
    position: "relative",
    width: "100%",
    height: "100%",
  },
  bg: {
    position: "absolute",
    top: 0,
    bottom: 0,
    right: 0,
    left: 0,
    background: `url(${bgUrl})`,
    backgroundRepeat: "no-repeat",
    backgroundPosition: "center",
    backgroundSize: "cover",

    filter: "grayscale(2%) brightness(40%)",
    WebkitFilter: "grayscale(20%) brightness(40%)",
    zIndex: -1,
  },
}));

const POLLING_INTERVAL = 3000;
export default function Gallery(props: {
  selectedImage: any | null;
  renderTaskId: string | null;
}) {
  const classes = useStyles(props);
  const { selectedImage } = props;
  const { renderTaskId } = props;
  const { loading, error, data, startPolling, stopPolling } = useQuery(
    GQL_GET_IMAGE_STATE,
    {
      variables: {
        getTaskId: renderTaskId,
      },
      pollInterval: POLLING_INTERVAL,
      onError: (e) =>
        console.log("error", `GQL_UPLOAD_IMAGE: ${JSON.stringify(e)}`),
    }
  );
  const [getMaskResults, masksRes] = useLazyQuery(GQL_GET_MASKS, {
    variables: {
      getTaskId: renderTaskId,
    },
    onError: (e) =>
      console.log("error", `GQL_UPLOAD_IMAGE: ${JSON.stringify(e)}`),
  });
  useEffect(() => {
    if (Boolean(renderTaskId)) {
      startPolling(POLLING_INTERVAL);
    } else {
      stopPolling();
    }
  }, [getMaskResults, renderTaskId, startPolling, stopPolling]);
  useEffect(() => {
    if (data && data.getTask) {
      getMaskResults();
      console.log("Reading masksRes")
      if ( data.getTask.taskFinished) stopPolling();
    }
  }, [data, getMaskResults, stopPolling]);

  return (
    <div className={classes.root}>
      <div className={classes.bg} />
      <ImageCard
        selectedImage={selectedImage}
        taskData={data}
        maskData={masksRes.data}
        loading={loading || masksRes.loading}
      />
    </div>
  );
}
