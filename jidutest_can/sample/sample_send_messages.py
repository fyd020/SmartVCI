import time
import logging
from jidutest_can.canapp import CanController
from jidutest_can.package import package_path


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
 

# 发送CAN裸数据（仅供参考）
def send_can_messages():  
    
    # 实例化一个控制器去发送裸数据
    # "BodyCAN"：控制器名字
    # "pcan"： 控制器采用的硬件设备类型（如PEAK公司的pcan）
    # 1: 控制器使用的硬件设备通道号（1, 2, ... , 16）
    # "v0.6.5/SDB22R04_BGM_BodyCAN_220923_Release.dbc"：dbc文件路径
    sender = CanController(
        "BodyCAN", 
        "pcan", 
        1,
        package_path.parent / r"test/resource/v1.0/v1.0/SDB23R01_BodyCAN_230316_Release.dbc"
    )
    
    # 连接硬件
    sender.connect()
    
    # 启动线程，开始发送裸数据
    # {0xb4: "00:00:00:00:35:94:00:09"}, {0xb8:"00:00:00:00:35:94:00:09"}： can_id和data组成的字典
    # is_fd: 是否是canfd
    sender.send_messages({0xb4: "00:00:00:00:35:94:00:09"}, {0xb8:"00:00:00:00:35:94:00:09"}, is_fd=False)
    
    # 等待60秒
    time.sleep(60)
    
    # 停止发送信号
    sender.stop_sending()
    
    # 断开硬件
    sender.disconnect()


if __name__ == "__main__":
    send_can_messages()
    