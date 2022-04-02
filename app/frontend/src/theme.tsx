import { createTheme } from "@material-ui/core/styles";

export const theme = createTheme({
  palette: {
    type: "light",
    primary: {
      main: "#5a189a",
    },
    secondary: {
      main: "#ff9e00",
    },
  },
  typography: {
    h2: {
      fontSize: "2.5rem",
      fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
      fontWeight: 200,
    },
    h1: {
      fontSize: "4.2rem",
      fontFamily: '"Poppins"',
    },
    body1: {
      fontFamily: '"Poppins"',
    },
    body2: {
      fontFamily: '"Poppins"',
    },
    h3: {
      fontFamily: '"Poppins"',
      fontSize: "1.8rem",
      fontWeight: 500,
    },
  },
});
