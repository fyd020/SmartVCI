import sys
import time
import logging
from jidutest_can.can import CanBus
from jidutest_can.can import RawMessage
from jidutest_can.canapp import CanController
from jidutest_can.canapp import CanLogManager

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

DI_DBC = r"test/test_smartvci/resources/DTSDI_C01_B04.dbc"

# 接受CAN裸数据（仅供参考）
def read_di_by_message(can_id, channel=1):  
    
    can_bus= CanBus(interface="smartvci", channel=channel, fd=False)

    can_controller = CanController(
        name="DTS_Tester",
        interface="smartvci",
        channel=channel,
        db_path=DI_DBC,
        bus=can_bus
    )
    can_controller.connect()
    
    # 发送一帧，（可以传多个信号，但是每个信号对应的报文只发送一帧
    can_controller.send_messages_once({can_id: "00:00:00:00:00:00:00:00"}, is_remote_frame=True, is_extended_frame=True)
    # can_controller.send_signals({"DTSDO_Channel_01_Output_Enable": True, "DTSDO_Channel_01_Output": "High"})
    # can_controller_1.send_signals_once({"DTSDO_Channel_01_Output_Enable": True, "DTSDO_Channel_01_Output": "High"})
    
    # 获取接收到的裸数据, 0xb8, 0xb4是想要接收的信号，num为最大接收的裸数据数, duration是最大接收时长
    result = can_controller.receive_messages(can_id, duration=1)
    
    # 打印接收到的裸数据列表
    print(result)
    
    # 断开硬件
    can_controller.disconnect()

# 接受CAN裸数据（仅供参考）
def read_di_by_signal(signal, channel=1):  
    
    can_bus= CanBus(interface="smartvci", channel=channel, fd=False)

    can_controller = CanController(
        name="DTS_Tester",
        interface="smartvci",
        channel=channel,
        db_path=DI_DBC,
        bus=can_bus
    )
    can_controller.connect()
    
    # 发送一帧，（可以传多个信号，但是每个信号对应的报文只发送一帧
    can_controller.send_messages_once({0xd114: "00:00:00:00:00:00:00:00"}, is_remote_frame=True, is_extended_frame=True)
    # can_controller.send_signals({"DTSDO_Channel_01_Output_Enable": True, "DTSDO_Channel_01_Output": "High"})
    # can_controller_1.send_signals_once({"DTSDO_Channel_01_Output_Enable": True, "DTSDO_Channel_01_Output": "High"})
    
    # 获取接收到的裸数据, 0xb8, 0xb4是想要接收的信号，num为最大接收的裸数据数, duration是最大接收时长
    result = can_controller.receive_signals(signal, duration=1)
    
    # 打印接收到的裸数据列表
    print(result)
    
    # 断开硬件
    can_controller.disconnect()
    
    
if __name__ == "__main__":
    # read_di_by_message(can_id=0xd114)
    read_di_by_signal(signal="DTSDI_Channel_01_Status")
        