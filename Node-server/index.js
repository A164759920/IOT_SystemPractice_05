let WebSocketServer = require("ws").Server,
  wss = new WebSocketServer({ port: 8188 });

wss.on("connection", function (ws) {
  ws.isAlive = true;
  ws.on("pong", function (msg) {
    console.log("msg", msg.toString());
  });
  ws.on("message", function (message) {
    console.log("接收", message.toString());
    // 非空消息
    if (message) {
      // 遍历客户端列表，原样转发数据
      wss.clients.forEach(function each(client) {
        client.send(message);
      });
    }
  });
});
wss.on("headers", (res) => {
  console.log("新客户端连接", res);
});
wss.on("error", (error) => {
  console.log("错误", error);
});
