import time
import logging
from jidutest_can import CanBus
from jidutest_can import CanController
from jidutest_can.can import PCANFD_500000_2000000


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


# 信号发送示例 (仅供参考)
def modify_ecu_sending_signals():
    
    # 实例化一个控制器接收某ecu发送的信号，并针对指定的信号值做修改，然后再发送修改后的和未修改的全部信号
    # "ConnectivityCANFD"：控制器名字
    # "pcan"： 控制器采用的硬件设备类型（如PEAK公司的pcan）
    # 1: 控制器使用的硬件设备通道号（1, 2, ... ）
    # "/root/pengtao/jidusdb/02-DBC/AddNmSigs/SDB23R01_ConnectivityCANFD_230116_Release.dbc"：dbc文件路径
    sender = CanController(
        "ConnectivityCANFD",
        "pcan", 
        7,
        r"/root/pengtao/jidusdb/02-DBC/AddNmSigs/SDB23R01_ConnectivityCANFD_230116_Release.dbc"
    )
    
    # 连接硬件
    sender.connect()
    
    bus = CanBus(interface="pcan", channel=5, fd=True, **PCANFD_500000_2000000)
    # "VehModMngtGlbSafe1PwrLvlElecMai"： 来自于dbc文件的信号名； 3：信号值
    # "AgDataRawSafeRollRate"： 来自于dbc文件的信号名； 2：信号值
    # 修改发送的信号值
    sender.modify_ecu_sending_signals({"VehModMngtGlbSafe1PwrLvlElecMai": 3}, {"AgDataRawSafeRollRate": 2}, send_bus=bus)

    # 等待30秒
    time.sleep(300)

    # 停止发送信号
    sender.stop_sending()
    time.sleep(5)
    
    # 断开硬件
    sender.disconnect()
    
    
if __name__ == "__main__":
    modify_ecu_sending_signals()
