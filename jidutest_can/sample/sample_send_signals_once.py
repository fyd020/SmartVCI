import time
import logging
from jidutest_can.canapp import CanController


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# 信号发送示例 (仅供参考)
def send_one_can_signal():
    
    # 实例化一个控制器去发送信号对应的一帧报文
    # "BodyCAN"：控制器名字
    # "pcan"： 控制器采用的硬件设备类型（如PEAK公司的pcan）
    # 1: 控制器使用的硬件设备通道号（1, 2, ... , 16）
    # "v0.6.5/SDB22R04_BGM_BodyCAN_220923_Release.dbc"：dbc文件路径
    sender = CanController(
        "BodyCAN", 
        "pcan", 
        1,
        r"/test/resource/v1.0/v1.0/SDB23R01_BodyCAN_230316_Release.dbc"
    )
    
    # 连接硬件
    sender.connect()
    
    # 发送一帧，（可以传多个信号，但是每个信号对应的报文只发送一帧）
    # "DoorOpenerPassReqTrigSrc"： 来自于dbc文件的信号名； 3：信号值
    # "DoorOpenerLeReReqDoorOpenerReq2"： 来自于dbc文件的信号名； 2：信号值
    sender.send_signals_once({"DoorOpenerPassReqTrigSrc": 3}, {"DoorOpenerLeReReqDoorOpenerReq2": 2})
    
    # 断开硬件
    sender.disconnect()
    
    
if __name__ == "__main__":
    send_one_can_signal()
