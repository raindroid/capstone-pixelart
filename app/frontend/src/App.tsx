import React, { useState } from "react";
import logo from "./logo.svg";
import "./App.css";
import PAppBar from "./components/PAppBar";
import UploadImage from "./components/UploadImage";
import { theme } from "./theme";
import { ThemeProvider } from "@material-ui/core/styles";
import Gallery from "./components/Gallary";
import { makeStyles } from "@material-ui/core/styles";
import { IconButton, Theme, Button } from "@material-ui/core";

import {
  ApolloClient,
  InMemoryCache,
  ApolloProvider,
  useQuery,
  gql,
} from "@apollo/client";
import { GQL_WAKE_PYTHON } from "./graphql/pixelart";

const client = new ApolloClient({
  uri: "https://pixelart.yucanwu.com/api/",
  cache: new InMemoryCache(),
});

const useStyles = makeStyles((theme: Theme) => ({
  rootContent: {
    position: "fixed",
    top: 50,
    bottom: 0,
    left: 0,
    right: 0,
    [theme.breakpoints.up("sm")]: {
      top: 72,
      bottom: 8,
      left: 8,
      right: 8,
    },
  },
}));

const imgSample =
  "https://images.unsplash.com/photo-1519255122284-c3acd66be602?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=795&q=80";

function App() {
  const classes = useStyles();
  const [selectedImage, setSelectedImage] = useState<any | null>(imgSample);
  const [renderTaskId, setRenderTaskId] = useState<string | null>(null);
  const { loading, error, data } = useQuery(GQL_WAKE_PYTHON);

  console.log(data);
  return (
    <ThemeProvider theme={theme}>
      <div className="App">
        <PAppBar />
        <div className={classes.rootContent}>
          <Gallery selectedImage={selectedImage} renderTaskId={renderTaskId} />

          <UploadImage
            renderTaskId={renderTaskId}
            setRenderTaskId={setRenderTaskId}
            selectedImage={selectedImage}
            setSelectedImage={setSelectedImage}
          />
        </div>
      </div>
    </ThemeProvider>
  );
}

export default function AppWithApollo() {
  return (
    <ApolloProvider client={client}>
      <App />
    </ApolloProvider>
  );
}
