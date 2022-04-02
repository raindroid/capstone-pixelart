const express = require("express");
const { ApolloServer, gql, graphqlConnect } = require("apollo-server-express");
const bodyParser = require("body-parser");
const typeDefs = require("./graphql/typeDefs");
const resolvers = require("./graphql/resolvers");
const mongoose = require("mongoose");
const path = require("path");
var cors = require('cors');

require('dotenv').config();

async function startServer() {
    const app = express();
    const port = process.env.PORT || 3000;
    const graphqlPath = process.env.GRAPHQL_URL || "/api";
    app.use(bodyParser.json({limit:'50mb'}));
    app.use(express.json({ limit: '50mb' }))
    app.use(cors());

    app.use(function(req, res, next) {
        console.log(`${new Date()} - ${req.method} request ${req.url}`);
        next(); // pass control to next handler
    })
  
    const apolloServer = new ApolloServer({
      typeDefs,
      resolvers,
    });
  
    await apolloServer.start();
    apolloServer.applyMiddleware({ app, path: graphqlPath });
  
    await mongoose.connect(process.env.DB_URL, {
      useUnifiedTopology: true,
      useNewUrlParser: true,
    });
    console.log("Mongoose Connected!");
  
    // Routes
    app.set("trust proxy", true);
  
    app.use("/api", function (req, res) {
      res.json({
        data: "API is preparing",
      });
    });
  
    // All other GET requests not handled before will return our React app
    app.use(express.static("../frontend/build"));
    app.get("*", (req, res) => {
      res.sendFile(path.resolve(__dirname, "../frontend/build", "index.html"));
    });
  
    app.listen(port, () => {
      console.log(`PixelArt (ECE496) app listening at http://localhost:${port}`);
    });
  }
  startServer();