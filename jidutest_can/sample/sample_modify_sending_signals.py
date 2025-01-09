import time
import logging
from jidutest_can import CanController


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# 信号发送示例 (仅供参考)
def modify_can_signals():
    
    # 实例化一个控制器去发送信号并在发送过程中改变信号值
    # "BodyCAN"：控制器名字
    # "pcan"： 控制器采用的硬件设备类型（如PEAK公司的pcan）
    # 1: 控制器使用的硬件设备通道号（1, 2, ... , 16）
    # "v0.6.5/SDB22R04_BGM_BodyCAN_220923_Release.dbc"：dbc文件路径
    sender = CanController(
        "BodyCAN", 
        "pcan", 
        1,
        r"D:\JiDU\jidutest\jidutest-sdk\jidutest-can\test\resource\v1.0\v1.0\SDB23R01_BodyCAN_230316_Release.dbc"
    )
    
    # 连接硬件
    sender.connect()
    
    # 启动线程，开始发送周期性信号
    # "DoorOpenerPassReqTrigSrc"： 来自于dbc文件的信号名； 3：信号值
    # "DoorOpenerLeReReqDoorOpenerReq2"： 来自于dbc文件的信号名； 2：信号值
    sender.send_signals({"DoorOpenerPassReqTrigSrc": 3}, {"DoorOpenerLeReReqDoorOpenerReq2": 2})
    
    # 等待30秒
    time.sleep(30)
    
    # 修改发送的信号值
    sender.modify_sending_signals({"DoorOpenerPassReqTrigSrc": 2})
    
    # 等待30秒
    time.sleep(30)
    
    # 停止发送信号
    sender.stop_sending()
    time.sleep(5)
    
    # 断开硬件
    sender.disconnect()
    
    
if __name__ == "__main__":
    modify_can_signals()
