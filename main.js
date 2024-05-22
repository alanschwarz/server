const WebSocket = require("ws");

const express = require("express");
const app = express();

// const hx711 = require("../hx711");
// const sensor = new hx711(5, 6);

app.get("/", (req, res) => {
  // serve the html file located in the parent directory
  res.sendFile(__dirname + "/app/index.html");
});

app.listen(3000, () => {
  console.log("Server running on port 3000");
});

const server = new WebSocket.Server({
  port: 8080,
  autoAcceptConnections: true,
  isBinary: false,
});

server.on("connection", (socket) => {
  socket.on("message", (message, isBinary) => {
    message = isBinary ? message.toString() : message;
    console.log(message.toString());

    switch (message.toString()) {
      case "tare":
        // sensor.tare();
        break;
      case "read":
        // socket.send(sensor.getUnits() ? sensor.getUnits().toFixed(1) : "0");
        socket.send((Math.random() * 100).toFixed(2));
        break;
      default:
        break;
    }
  });
});
