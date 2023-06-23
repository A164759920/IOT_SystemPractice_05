let WebSocketServer = require("ws").Server,
  wss = new WebSocketServer({ port: 8188 });

wss.on("connection", function (ws) {
  ws.isAlive = true;
  ws.on("pong", function (msg) {
    console.log("msg", msg.toString());
  });
    ws.on("message", function (message) {
      console.log("接收",message.toString())
    wss.clients.forEach(function each(client) {
      // 原样转发数据
      client.send(message);
    });
  });
});
// const interval = setInterval(function ping() {
//   wss.clients.forEach(function each(ws) {
//     // if (ws.isAlive === false) return ws.terminate();
//     // ws.isAlive = false;
//     ws.ping("ping");
//   });
// }, 5 * 1000);

wss.on("headers", (res) => {
  console.log("头部", res);
});
wss.on("error", (error) => {
  console.log("错误");
});
