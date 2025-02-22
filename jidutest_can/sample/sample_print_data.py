from jidutest_can.canapp import CanController
from jidutest_can.canapp import CanLogManager
from jidutest_can.can import Notifier
import logging
import time


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# 打印数据
def print_can_data():
    
    # 实例化一个控制器去打印数据到控制台
    # "BodyCAN"：控制器名字
    # "pcan"： 控制器采用的硬件设备类型（如PEAK公司的pcan）
    # 1: 控制器使用的硬件设备通道号（1, 2, ... , 16）
    # "v0.6.5/SDB22R04_BGM_BodyCAN_220923_Release.dbc"：dbc文件路径
    printer = CanController(
        "BodyCAN", 
        "pcan", 
        1,
        db_path=r"D:\JiDU\jidutest\jidutest-sdk\jidutest-can\test\resource\v1.0\SDB23R01_ConnectivityCANFD_230116_Release.dbc"
    )
    printer.connect()
    
    # 实例化一个CAN日志管理器, 传入的参数为上面实例化的控制器中的bus，或者自己实例化一个bus也可以
    manager = CanLogManager(printer.bus)
    
    # 开始打印接收到的数据
    # 如果传入一个file参数，则不会打印到控制台，会保存成一个txt格式文件
    manager.start_printing(r"./printer.txt")
    
    # 打印4s
    time.sleep(4)
    
    # 停止打印数据
    manager.stop_printing()
   
    
if __name__ == "__main__":
    print_can_data()
