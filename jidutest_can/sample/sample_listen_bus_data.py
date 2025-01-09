import time
import logging
from jidutest_can import CanBus
from jidutest_can import CanLogManager
from jidutest_can.can import PCANFD_500000_2000000
from jidutest_can.canapp import CanController


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
 

# 对willow平台暴露的接口和使用方式（仅供参考）
def listen_bus_data():
    
    # 实例化一个控制器
    # "ConnectivityCANFD"：控制器名字
    # "pcan"： 控制器采用的硬件设备类型（如PEAK公司的pcan）
    # 1: 控制器使用的硬件设备通道号（1, 2, ... , 16）
    # 可以传dbc文件路径或者自己实例化好的bus，但是以传入的dbc优先级最高
    # 实例化一个bus
    bus1 = CanBus(interface="pcan", channel=1, fd=True, **PCANFD_500000_2000000)
    bus2 = CanBus(interface="pcan", channel=2, fd=True, **PCANFD_500000_2000000)
    receiver = CanController(
        "BodyCAN",
        "pcan", 
        1,
        # r"D:\JiDU\jidutest\jidutest-sdk\jidutest-can\test\resource\v1.0\SDB23R01_BodyCAN_230116_Release.dbc",
        bus=bus1
    )
    receiver1 = CanController(
        "ConnectivityCANFD",
        "pcan", 
        2,
        # r"D:\JiDU\jidutest\jidutest-sdk\jidutest-can\test\resource\v1.0\SDB23R01_ConnectivityCANFD_230116_Release.dbc",
        bus=bus2
    )
    # 连接硬件，并实例化Notify对象
    receiver.connect()
    receiver1.connect()
    # 实例化抓取log管理对象
    manager = CanLogManager([bus1, bus2])
    # 开始log录制
    manager.start_logging(f"demo{int(time.time()*1000)}.asc")
    receiver.listen_messages()  # 可以接收裸数据/信号，接收时长全款自己后面sleep
    time.sleep(1)
    received_raw_messages1 = receiver.get_received_signals(10)  # 获取解析后的数据
    logger.info(received_raw_messages1.qsize())
    time.sleep(1)
    received_raw_messages2 = receiver.get_received_raw_messages(5)
    logger.info(received_raw_messages2.qsize())
    time.sleep(1)
    received_raw_messages3 = receiver.get_received_signals()  # 获取解析后的数据
    logger.info(received_raw_messages3.qsize())
    time.sleep(1)
    received_raw_messages4 = receiver.get_received_raw_messages(5)
    logger.info(received_raw_messages4.qsize())
    time.sleep(1)

    # 停止log录制
    manager.stop_logging()
    # 断开硬件，并停止接收，并清空buffer
    receiver.disconnect()
    time.sleep(5)
    received_raw_messages5 = receiver.get_received_raw_messages()
    logger.info(received_raw_messages5.qsize())
    
    
if __name__ == "__main__":
    listen_bus_data()
        