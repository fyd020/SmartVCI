import logging
from jidutest_can.canapp import CanController


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
 

# 接受CAN裸数据（仅供参考）
def receive_one_can_message():  
    
    # 实例化一个控制器去接收一个裸数据
    # "BodyCAN"：控制器名字
    # "pcan"： 控制器采用的硬件设备类型（如PEAK公司的pcan）
    # 2: 控制器使用的硬件设备通道号（1, 2, ... , 16）
    # "v0.6.5/SDB22R04_BGM_BodyCAN_220923_Release.dbc"：dbc文件路径
    receiver = CanController(
        "ConnectivityCANFD",
        "pcan", 
        1,
        db_path=r"D:\JiDU\jidutest\jidutest-sdk\jidutest-can\test\resource\v1.0\SDB23R01_ConnectivityCANFD_230116_Release.dbc"
    )
    
    # 连接硬件
    receiver.connect()
    
    # 获取接收到的一个裸数据, 0xb8是想要接收的信号，timeout是最大接收时长
    result = receiver.receive_message_once(0xb8, timeout=5)
    
    # 打印接收到的裸数据
    print(result)
    
    # 断开硬件
    receiver.disconnect()
    
    
if __name__ == "__main__":
    receive_one_can_message()
        