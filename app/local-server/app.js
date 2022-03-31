let express = require('express');
let app = express();
require('dotenv').config();

app.use(function(req, res, next) {
    console.log(`${new Date()} - ${req.method} request ${req.url}`);
    next(); // pass control to next handler
})

app.use(express.static(path.join(__dirname, '/static/')));

const port = process.env.PORT || 3000;
app.listen(port, function() {
    console.log(`Server started on port ${port}`);
})