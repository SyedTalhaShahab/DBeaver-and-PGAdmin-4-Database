// 1. Install the required dependencies
// 2. npm install express
// 3. Create a file named app.js in the FrontEnd folder and set up a basic Express server to serve your static files
// 4. Start the front-end server: node app.js
/*
this file is not the middle man
*/
const express = require("express");
const path = require("path");

const app = express();
const PORT = 3000; // Port for the front-end server

// Serve static files
app.use(express.static(path.join(__dirname)));

// Default route to serve main.html
app.get("/", (req, res) => {
    res.sendFile(path.join(__dirname, "index.html"));
});

app.listen(PORT, () => {
    console.log(`Front-end server is running on http://localhost:${PORT}`);
});
