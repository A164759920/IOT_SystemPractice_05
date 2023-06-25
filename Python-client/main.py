import asyncio
import threading

import websockets
import random
import RPi.GPIO as GPIO
import time

# ######################### RASPBERRY_PART ######################### #

makerobo_RelayPin = 13  # 定义继电器管脚为Pin13
makerobo_TRIG = 11  # 超声波模块Tring控制管脚
makerobo_ECHO = 12  # 超声波模块Echo控制管脚
makerobo_BeepPin = 16

max_distance = 25
current_distance = 0
relay_state = False
relay_lock_state = "relay_lock_normal"  # relay_lock_on relay_lock_normal relay_lock_off
relay_thread = None

# 初始化工作
def makerobo_setup():
    global BEEP
    GPIO.setmode(GPIO.BOARD)  # 采用实际的物理管脚给GPIO口
    # GPIO.setwarning(False)  # 去除GPIO警告

    # 继电器初始化
    GPIO.setup(makerobo_RelayPin, GPIO.OUT)  # 设置Pin模式为输出模式
    GPIO.output(makerobo_RelayPin, GPIO.LOW)  # 关闭继电器

    # 超声波初始化
    GPIO.setup(makerobo_TRIG, GPIO.OUT)  # Tring设置为输出模式
    GPIO.setup(makerobo_ECHO, GPIO.IN)  # Echo设置为输入模式

    # 蜂鸣器初始化
    GPIO.setup(makerobo_BeepPin, GPIO.OUT, initial= GPIO.HIGH)



# 释放资源
def makerobo_destroy():
    GPIO.output(makerobo_RelayPin, GPIO.LOW)  # 关闭继电器
    GPIO.cleanup()  # 释放资源


# # 超声波计算距离函数
def ur_disMeasure():
    GPIO.output(makerobo_TRIG, 0)  # 开始起始
    time.sleep(0.000002)  # 延时2us

    GPIO.output(makerobo_TRIG, 1)  # 超声波启动信号，延时10us
    time.sleep(0.00001)  # 发出超声波脉冲
    GPIO.output(makerobo_TRIG, 0)  # 设置为低电平

    while GPIO.input(makerobo_ECHO) == 0:  # 等待回传信号
        us_a = 0
    us_time1 = time.time()  # 获取当前时间
    while GPIO.input(makerobo_ECHO) == 1:  # 回传信号截止信息
        us_a = 1
    us_time2 = time.time()  # 获取当前时间

    us_during = us_time2 - us_time1  # 转换微秒级的时间

    # 声速在空气中的传播速度为340m/s, 超声波要经历一个发送信号和一个回波信息，
    # 计算公式如下所示：
    return us_during * 340 / 2 * 100  # 求出距离


# 继电器自动控制器
def relay_controller(distance):
    # 超出距离,关闭继电器
    # while True:
    global relay_state, relay_lock_state
    if relay_lock_state == "relay_lock_on":
        print("常开控制")
        # GPIO.output(makerobo_BeepPin, GPIO.LOW)
        relay_state = True
    if relay_lock_state == "relay_lock_off":
        print("常闭控制")
         #GPIO.output(makerobo_BeepPin, GPIO.LOW)
        relay_state = False
    if relay_lock_state == "relay_lock_normal":
        print("正常控制")
        if distance >= max_distance:
            GPIO.output(makerobo_RelayPin, GPIO.LOW)
            relay_state = False
        if distance <= max_distance:
            GPIO.output(makerobo_RelayPin, GPIO.HIGH)
            relay_state = True



async def create_disThread_loop():
    global current_distance
    while True:
        # us_dis = random.randint(20, 30)
        us_dis = ur_disMeasure()  # 获取超声波计算距离
        print("距离", us_dis)
        current_distance = us_dis
        relay_controller(current_distance)
        GPIO.output(makerobo_BeepPin, GPIO.HIGH)
        await asyncio.sleep(1)

# ######################### WEBSOCKETS ######################### #

wsServer = "ws://192.168.43.72:8188/"
global_ws = None

def createDataFrame(dataType, payload):
    frame = "rasp," + str(dataType) + "," + str(payload)
    return frame

async def on_message(message):
    print("Received message:", message)

async def on_error(error):
    print("WebSocket error:", error)

async def on_close():
    print("WebSocket connection closed")

def msg_handler(message):
    global relay_state, relay_lock_state
    decoded_message = message.decode()
    # 解析数据帧
    if "," in decoded_message:
        parts = decoded_message.split(",")
        clientName = parts[0]
        clientFunc = parts[1]
        clientPayload = parts[2]
    else:
        clientName = ""
        clientFunc = ""
        clientPayload = ""
    if clientName == "H5":
        if clientFunc == "command":

            if clientPayload == "relay_lock_on":
                print("常开继电器")
                GPIO.output(makerobo_BeepPin, GPIO.LOW)
                GPIO.output(makerobo_RelayPin, GPIO.HIGH)
                relay_lock_state = clientPayload

            if clientPayload == "relay_lock_off":
                print("常闭继电器")
                GPIO.output(makerobo_BeepPin, GPIO.LOW)
                GPIO.output(makerobo_RelayPin, GPIO.LOW)
                relay_lock_state = clientPayload

            if clientPayload == "relay_lock_normal":
                print("自控继电器")
                GPIO.output(makerobo_BeepPin, GPIO.HIGH)
                if relay_lock_state == "relay_lock_on" or relay_lock_state == "relay_lock_off":
                    GPIO.output(makerobo_BeepPin,GPIO.LOW)
                relay_lock_state = clientPayload

            if clientPayload == "relay_on":
                print("打开继电器")
                GPIO.output(makerobo_RelayPin, GPIO.HIGH)
                relay_state = True

            if clientPayload == "relay_off":
                print("关闭继电器")
                GPIO.output(makerobo_RelayPin, GPIO.LOW)
                relay_state = False


    # else:
    #     print("非H5不处理")


async def send_message(websocket):
    global relay_state, current_distance
    while True:
        # 模拟需要发送的数据，这里使用字符串 "data" 作为示例
        dis_data = createDataFrame("data_dis", current_distance)
        print(dis_data)
        # 发送数据到服务器
        await websocket.send(dis_data)
        if relay_state:
            relay_data = createDataFrame("state_dis", "relay_on")
        else:
            relay_data = createDataFrame("state_dis", "relay_off")
        await websocket.send(relay_data)
        # 等待一秒
        await asyncio.sleep(1)


async def receive_message(websocket):
    while True:
        # 接收服务器发送的数据
        message = await websocket.recv()
        msg_handler(message)


async def connect_websocket():
    try:
        async with websockets.connect(wsServer) as ws:
            global global_ws
            global_ws = ws
            disThread_task = asyncio.ensure_future(create_disThread_loop())
            tasks = [send_message(ws), receive_message(ws), disThread_task]
            await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        await on_close()
    except Exception as e:
        await on_error(e)
       #  makerobo_destroy()


if __name__ == '__main__':
    makerobo_setup()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(connect_websocket())
    loop.close()
