import sys
import time
import logging
from jidutest_can.can import CanBus
from jidutest_can.can import RawMessage
from jidutest_can.canapp import CanController
from jidutest_can.canapp import CanLogManager


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
 
DO_DBC = r"/root/dading/jidutest-can/test_smartvci/resources/DTSDO_C01_B05.dbc"

# 接受CAN裸数据（仅供参考）
def write_do_by_message(message, channel=1):  
    
    can_bus= CanBus(interface="smartvci", channel=channel, fd=False)

    can_controller = CanController(
        name="DTS_Tester",
        interface="smartvci",
        channel=channel,
        db_path=DO_DBC,
        bus=can_bus
    )
    can_controller.connect()
    
    # 发送一帧，（可以传多个信号，但是每个信号对应的报文只发送一帧）
    # can_controller.send_messages_once({0xd013: "00:FF:00:00:FF:FF:00:00"}, is_fd=False)
    can_controller.send_messages_once(message, is_extended_frame=True)
    # can_controller_1.send_signals_once({"DTSDO_Channel_01_Output_Enable": True, "DTSDO_Channel_01_Output": "High"})
    
    # 打印接收到的裸数据列表
    time.sleep(1)
    
    # 断开硬件
    can_controller.disconnect()

# 接受CAN裸数据（仅供参考）
def write_do_by_signal(signal, channel=1):  
    
    can_bus= CanBus(interface="smartvci", channel=channel, fd=False)

    can_controller = CanController(
        name="DTS_Tester",
        interface="smartvci",
        channel=channel,
        db_path=DO_DBC,
        bus=can_bus
    )
    can_controller.connect()
    
    # 发送一帧，（可以传多个信号，但是每个信号对应的报文只发送一帧）
    # can_controller.send_messages_once({0xa117: "FF:FF:FF:FF:FF:FF:FF:3F"}, is_extended_frame=True)
    can_controller.send_signals_once(signal)
    
    # 打印接收到的裸数据列表
    time.sleep(1)
    
    # 断开硬件
    can_controller.disconnect()
    
    
if __name__ == "__main__":
    # write_do_by_message(message={0xd017: "00:FF:FF:FF:FF:FF:FF:3F"})
    write_do_by_signal(signal={
        "DTSDO_Channel_01_Output_Enable": True, 
        "DTSDO_Channel_01_Output": "High",
        "DTSDO_Channel_02_Output_Enable": True, 
        "DTSDO_Channel_02_Output": "High",
    })
        