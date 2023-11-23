# CAN-CONTROL-RMD-L-9015

RMD-L-9015 CAN 通信的接口封装。写了 `ESP32+TJA1050` 和 `ZLG` 的封装

## ESP32

ESP32 CAN 控制 `RMD-L-9015`，把文档的通信协议翻译了成 `twai_message_t` 的格式

ESP32 IO4 连接 TJA1050 RX

ESP32 IO5 连接 TJA1050 TX

如果不一致需要在代码中更改

## ZLG-Python

USB 转 CAN 控制 `RMD-L-9015`，把文档的通信协议翻译了成 ZLG 的格式

周立功以及可以使用周立功驱动的兼容设备

功能封装在 `ZLG-Python/CanControlRMD.py` 下

实现了部分单电机控制命令、运动控制模式命令、CAN监听线程等功能

### 友情链接

[周立功官网二次开发资料](https://manual.zlg.cn/web/#/152?page_id=5332)

[CSDN上的ZLG Python开发资料](https://blog.csdn.net/weifengdq/article/details/117482461)