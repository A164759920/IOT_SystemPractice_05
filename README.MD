# 一.websocket 三端

## ①.Vue-client H5-ws-client

- 仅给出**Vue2**单文件

## ②.Node-server 本地 node-ws-server

- 使用前 CD 到目录并**npm init**

## ③.Python-client RaspiBerry-ws-client

- 使用前安装对应的**依赖**

# 二. 数据帧格式解析

**数据帧主要分为 \***clientName**_、 _**clientFunc**\_、 \***clientPayloa**\*三部分.**

- **clientName**：用于标识发出该数据帧的客户端。
  - **_H5_**：表示该帧由手机 Web 端发出。
  - **_rasp_**：表示该帧由树莓派端发出。
- **clientFunc**：用于标识该数据帧的用途。
  - **_command_**：表示该帧是用于控制模式切换的命令帧，由 Web 端发出。
  - **_data_dis_**：表示该帧是用于上报测距数据的数据帧，由树莓派端发出。
  - **_state_dis_**：表示该帧是用于上报继电器闭合情况的数据帧，由树莓派发出。
- **clientPayload**：用于存储该数据帧的真实数据载荷。
  - **_relay_on_**：作为**state_dis**的可选项，表示继电器处于闭合状态。
  - **_relay_off_**：作为**state_dis**的可选项，表示继电器处于断开状态。
  - **_real_distance_**：作为“data_dis”的数据载荷，实际场景下替换为真实测距数据。
  - **_relay_lock_on_**：作为**command**的可选项，表示将控制模式切换为 **“常开”**。
  - **_relay_lock_off_**：作为**command**的可选项，表示将控制模式切换为 **“常闭”**。
  - **_relay_lock_normal_**：作为**command**的可选项，表示将控制模式切换为 **“自动控制”**。
