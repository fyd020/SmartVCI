import logging
from jidutest_can.can import CanBus
from jidutest_can.canapp import CanController
from jidutest_can.canapp import CanLogManager


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
 

# 接受CAN裸数据（仅供参考）
def receive_can_messages():  
    
    can_controllers = list()
    can_buses = list()
    can_bus_1 = CanBus(interface="smartvci", channel=1, fd=False)
    can_bus_2 = CanBus(interface="smartvci", channel=2, fd=False)
    # can_bus = CanBus(interface="smartvci", channel=1, fd=True, **PCANFD_500000_2000000)
    can_buses.append(can_bus_1)
    can_buses.append(can_bus_2)

    can_controller_1 = CanController(
        name="DTS_Tester",
        interface="smartvci",
        channel=1,
        db_path=r"/root/dading/jidutest-can/test_smartvci/resources/DTSDO_C01_B03.dbc",
        bus=can_bus_1
    )
    can_controller_2 = CanController(
        name="DTS_Tester",
        interface="smartvci",
        channel=2,
        db_path=r"/root/dading/jidutest-can/test_smartvci/resources/DTSDO_C01_B03.dbc",
        bus=can_bus_2
    )
    can_controllers.append(can_controller_1)
    can_controllers.append(can_controller_2)
    can_controller_1.connect()
    can_controller_2.connect()
    
    # 发送一帧，（可以传多个信号，但是每个信号对应的报文只发送一帧）
    # "DoorOpenerPassReqTrigSrc"： 来自于dbc文件的信号名； 3：信号值
    # "DoorOpenerLeReReqDoorOpenerReq2"： 来自于dbc文件的信号名； 2：信号值
    can_controller_1.send_messages({0xd013: "00:FF:00:00:FF:FF:00:00"}, is_fd=False)
    can_controller_1.send_messages_once({0xd013: "00:FF:00:00:FF:FF:00:00"}, is_fd=False)
    can_controller_1.send_signals({"DTSDO_Channel_01_Output_Enable": True, "DTSDO_Channel_01_Output": "High"})
    can_controller_1.send_signals_once({"DTSDO_Channel_01_Output_Enable": True, "DTSDO_Channel_01_Output": "High"})
    
    # 获取接收到的裸数据, 0xb8, 0xb4是想要接收的信号，num为最大接收的裸数据数, duration是最大接收时长
    result = can_controller_2.receive_messages(0xd017, duration=5)
    
    # 打印接收到的裸数据列表
    # print(result)

    # 停止发送信号
    can_controller_1.stop_sending()
    
    # 断开硬件
    can_controller_1.disconnect()
    can_controller_2.disconnect()
    
    
if __name__ == "__main__":
    receive_can_messages()
        