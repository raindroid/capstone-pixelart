import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import Typography from "@material-ui/core/Typography";
import Button from "@material-ui/core/Button";
import IconButton from "@material-ui/core/IconButton";
import MenuIcon from "@material-ui/icons/Menu";

const useStyles = makeStyles((theme) => ({
  root: {
    flexGrow: 1,
  },
  menuButton: {
    marginRight: theme.spacing(2),
  },
  appBar: {
    [theme.breakpoints.down("sm")]: {
      maxHeight: 72,
    },
    [theme.breakpoints.down("xs")]: {
      maxHeight: 50,
    },
  },
  title: {
    flexGrow: 1,
    [theme.breakpoints.down("sm")]: {
      fontSize: "1.8rem",
    },
    [theme.breakpoints.down("xs")]: {
      fontSize: "1.2rem",
    },
  },
  iconLogo: {
    maxHeight: "2rem",
    maxWidth: "2rem",
    paddingRight: "1rem",
    [theme.breakpoints.down("sm")]: {
      maxHeight: "1.4rem",
      maxWidth: "1.4rem",
      paddingRight: "0.8rem",
    },
    [theme.breakpoints.down("xs")]: {
      maxHeight: "1rem",
      maxWidth: "1rem",
      paddingRight: "0.8rem",
    },
  },
}));

export default function ButtonAppBar() {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <AppBar position="fixed" className={classes.appBar}>
        <Toolbar>
          <Typography variant="h2" className={classes.title}>
            <img className={classes.iconLogo} src="./favicon.png" alt="LOGO" />
            PixelArt
          </Typography>
        </Toolbar>
      </AppBar>
    </div>
  );
}
