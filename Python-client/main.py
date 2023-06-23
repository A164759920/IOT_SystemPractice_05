wsServer = "ws://127.0.0.1:8188/"
import asyncio
import websockets

async def on_message(message):
    print("Received message:", message)

async def on_error(error):
    print("WebSocket error:", error)

async def on_close():
    print("WebSocket connection closed")

# async def send_msg(webSocket):


async def connect_websocket():
    async with websockets.connect(wsServer) as ws:
        while True:
            try:
                # 发送消息到服务器
                await ws.send("Hello from client")
                message = await ws.recv()

                await on_message(message)



            except websockets.ConnectionClosed:
                await on_close()
                break
            except Exception as e:
                await on_error(e)

# 创建并运行事件循环
loop = asyncio.get_event_loop()
loop.run_until_complete(connect_websocket())

