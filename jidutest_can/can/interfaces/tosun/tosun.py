# -*- coding: utf-8 -*-
"""
@File        : cn_bus.py
@Author      : pengtao.li_ext@external.jiduauto.com
@Time        : 2023/06/06 09:57
@Update Time :
@Description : ToSun can Bus Class

"""
import queue
import time
import typing
from jidutest_can.can.interfaces.bus import BusABC
from jidutest_can.can.interfaces.util import channel2int
from jidutest_can.can.tools import CanOperationError
from jidutest_can.can.tools import CanInitializationError
from jidutest_can.cantools.database.message import Message
from jidutest_can.can.tools.bit_timing import BitTiming
from jidutest_can.can.tools.bit_timing import BitTimingFd
from jidutest_can.can.interfaces.tosun.constants import TOSUNCANFD_500000_2000000
from jidutest_can.can.interfaces.tosun.define_tosun import *
from jidutest_can.can.interfaces.tosun.define_tosun import _is_windows


logger = logging.getLogger(__file__)


class ToSunCanOperationError(CanOperationError):
    """Like :class:`can.exceptions.CanOperationError`, but specific to ToSun."""


class ToSunBus(BusABC):
    """
    与同星设备建立连接，并操作对应的can总线
    """

    def __init__(
            self,
            channel: int = 1,
            timing: typing.Optional[typing.Union[BitTiming, BitTimingFd]] = None,
            bitrate: int = 500000,
            *args,
            **kwargs,
    ) -> None:
        """
        功能说明：
            与同星设备建立连接，并实例化can总线
        参数说明：
            :param channel: 总线通道
            :param bitrate: 总线通道波特率，单位是bit/s，默认值为 500k bit/s
            :param date_brp: Clock prescaler for fast data time quantum，单位是bit/s，默认值为 2M bit/s,仅当使用CAN-FD时有用
            :param enable120: 设置硬件终端电阻器，默认为True
            :param fd: Should the Bus be initialized in CAN-FD mode. default is False
            :param mode: 读取总线数据方式，READ_TX_RX_DEF.TX_RX_MESSAGES(receive msg inclued tx and rx msg),
                         READ_TX_RX_DEF.TX_RX_MESSAGES(only receive rx msg)
        异常说明：无
        返回值：None
        """
        self.send_mags = list()
        self.message_cycles_list: typing.List[typing.Tuple[Message, typing.Set]] = list()
        self.received_raw_messages: queue.Queue = queue.Queue(2 ** 24)
        self.ADeviceHandle = c_size_t(0)
        self.initialize()
        self.device_count = self.scan_device()
        self.__timing = timing
        self.fd = isinstance(timing, BitTimingFd) if timing else kwargs.get("fd", False)
        channel = channel2int(channel)
        self.channel = channel
        self.manufacturer = self.product = self.serial = None
        self.channels = list()
        self.device_info = self.get_device_info()
        if not self.device_info:
            raise CanInitializationError(f"The connected TOSUN device does not have a can channel."
                                         f"Please check and try again.")
        if channel not in self.channels:
            raise CanOperationError(f"'channel' argument only be selected from {self.channels}, "
                                    f"it shouldn't be {channel}")
        self.connected = False
        self.init_counter: bool = True
        self.__mode = kwargs.get("mode", READ_TX_RX_DEF.TX_RX_MESSAGES)
        self.__can_data = list()
        enable120 = kwargs.get("enable120", True)
        self.__enable120 = A120.ENABLEA120 if enable120 else A120.DEABLEA120
        self.__bitrate = c_double(bitrate / 1000)
        self.__data_brp = c_double(kwargs.get("date_brp", 2000000) / 1000)
        self.channel_info = "TOSUN_CANBUS" + str(channel)
        super().__init__(channel=channel, bitrate=bitrate, *args, **kwargs)
        if kwargs.get("show"):
            return
        self.connect()
        self.configure()
        self.flush_rx_buffer()
        self.flush_tx_buffer()

    def initialize(self, AEnableFIFO=True, AEnableTurbe=True):
        """
        初始化函数（是否使能fifo,是否濢 活极速模式）
        """
        initialize_lib_tsmaster(AEnableFIFO, AEnableTurbe, True)
        logger.info(f"Initialize lib tsmaster.")

    def uninitialize(self):
        """
        释放函数
        """
        finalize_lib_tscan()
        logger.info(f"Finalize lib tsmaster.")

    def scan_device(self):
        a_device_scan = c_uint32(0)
        tscan_scan_devices(byref(a_device_scan))
        device_count = a_device_scan.value
        if not device_count:
            raise CanInitializationError(f'TOSUN device is not connected.')
        return device_count

    def get_device_info(self, ADeviceIdx: int = None) -> typing.List[list]:
        """
        功能说明：
            获取同星设备信息和所需通道数量
        参数说明：
            :param ADeviceIdx:设备索引
        异常说明：无
        返回值：设备信息和所需通道列表
        """
        device_info = list()
        for_list = range(self.device_count)
        all_channel_count = 0
        if ADeviceIdx is not None:
            for_list = for_list[ADeviceIdx:ADeviceIdx + 1]
        if not for_list:
            raise ValueError(f"Parameter 'ADeviceIdx' error,values can only be {list(for_list)}")
        for i in for_list:
            f_manufacturer = POINTER(c_char_p)()
            f_product = POINTER(c_char_p)()
            f_serial = POINTER(c_char_p)()
            ret1 = tscan_get_device_info(i, byref(f_manufacturer), byref(f_product), byref(f_serial))
            if ret1 == 0:
                f_manufacturer = string_at(f_manufacturer).decode("utf8")
                f_product = string_at(f_product).decode("utf8")
                f_serial = string_at(f_serial).decode("utf8")
                ret = tscan_connect(f_serial.encode('utf-8'), byref(self.ADeviceHandle))
                if ret not in (0, 5):
                    desc = tscan_get_error_description(ret)
                    logger.debug(f"TSMaster connect {f_manufacturer, f_product, f_serial} error: {desc}")
                else:
                    channel_count = tscan_get_can_channel_count(self.ADeviceHandle)
                    if channel_count:
                        channels = list(range(all_channel_count + 1, all_channel_count + channel_count + 1))
                        self.channels.extend(channels)
                        if not self.serial and self.channel in channels:
                            self.channel = channels.index(self.channel)
                            self.manufacturer = f_manufacturer
                            self.product = f_product
                            self.serial = f_serial
                        device_info.append([f_manufacturer, f_product, f_serial, channels])
                        all_channel_count += channel_count
                    if not ret:
                        tscan_disconnect_by_handle(self.ADeviceHandle)
            else:
                desc = tscan_get_error_description(ret1)
                logger.error(f"TSCAN get device info failed: {desc}")
        return device_info

    def connect(self) -> int:
        """
        功能说明：
            与同星设备建立连接
        参数说明：无
        异常说明：无
        返回值：连接的结果
        """
        ret = tscan_connect(self.serial.encode('utf-8'), byref(self.ADeviceHandle))
        if ret not in (0, 5):
            desc = tscan_get_error_description(ret)
            logger.error(f"TSMaster connect {self.manufacturer, self.product, self.serial} error: {desc}")
            raise CanInitializationError
        else:
            logger.info(f"Successfully Connected to TOSUN device.")
        self.connected = True
        return ret

    def disconnect(self):
        """
        断开指定硬件连接
        """
        if self.connected:
            ret = tscan_disconnect_by_handle(self.ADeviceHandle)
            if ret not in [0, 3]:
                desc = tscan_get_error_description(ret)
                logger.error(f"TSMaster disconnect by handle error: {desc}")
            else:
                logger.info(f"Successfully disconnected from TOSUN device.")
                self.connected = False
        else:
            logger.info(f"It has been disconnected from TOSUN device, does not need to be disconnected again.")

    def reset(self) -> None:
        self.disconnect()
        self.connect()

    def disconnect_all_devices(self):
        """
        断开本次所有的硬件设备连接
        """
        ret = tscan_disconnect_all_devices()
        if ret != 0:
            desc = tscan_get_error_description(ret)
            logger.error(f"TSMaster disconnect all devices error: {desc}")
        else:
            logger.info(f"Successfully disconnected from all TOSUN device.")

    def configure(self):
        if self.fd:
            ret = configure_canfd_baudrate(
                self.ADeviceHandle,
                self.channel,
                self.__bitrate,
                self.__data_brp,
                TLIBCANFDControllerType.lfdtISOCAN,
                TLIBCANFDControllerMode.lfdmNormal,
                self.__enable120
            )
            if ret != 0:
                desc = tscan_get_error_description(ret)
                raise CanInitializationError(f"TSMaster configure canfd baudrate error: {desc}")
            else:
                logger.info(f"Successfully configure canfd baudrate.")
            if _is_windows:
                # 下面方法在Linux中没有此方法
                if not self.__timing:
                    self.__timing = TOSUNCANFD_500000_2000000
                ret = configure_canfd_regs(
                    self.ADeviceHandle,
                    self.channel,
                    self.__bitrate,
                    self.__timing.nom_tseg1,
                    self.__timing.nom_tseg2,
                    self.__timing.nom_brp,
                    self.__timing.nom_sjw,
                    self.__data_brp,
                    self.__timing.data_tseg1,
                    self.__timing.data_tseg2,
                    self.__timing.data_brp,
                    self.__timing.data_sjw,
                    TLIBCANFDControllerType.lfdtISOCAN,
                    TLIBCANFDControllerMode.lfdmNormal,
                    self.__enable120
                )
                if ret != 0:
                    desc = tscan_get_error_description(ret)
                    logger.error(f"TSMaster configure canfd regs error: {desc}")
                else:
                    logger.info(f"Successfully configure canfd regs.")
        else:
            ret = configure_can_baudrate(self.ADeviceHandle,
                                         self.channel,
                                         self.__bitrate,
                                         self.__enable120)
            if ret != 0:
                desc = tscan_get_error_description(ret)
                logger.error(f"TSMaster configure can baudrate error: {desc}")
            else:
                logger.info(f"Successfully configure can baudrate.")

    def callback_recv(self, raw_message: RawMessage) -> typing.Optional[RawMessage]:
        """Block waiting for a message from the Bus.

            :param raw_message:
                callback on_rx_tx_can method received raw_massage

            :return:
                :obj:`None` on timeout or a :class:`~can.RawMessage` object.
        """

        if raw_message and self._matches_filters(raw_message):
            return raw_message
        else:
            return None

    def _recv_internal(
            self, timeout: typing.Optional[float] = None
    ) -> typing.Tuple[typing.Optional[RawMessage], bool]:
        # if self.fd:
        # TODO: 此处在使用can msg结构和方法收取can数据时，会收不到任何数据，暂时使用canfd格式和方法
        fr_raw = (TLibCANFD * 1)()
        recv_fun = receive_canfd_msgs
        # else:
        #     fr_raw = (TLibCAN * 1)()
        #     recv_fun = receive_can_msgs

        start_time = time.perf_counter()
        while timeout is None or time.perf_counter() - start_time <= timeout:
            buffersize = c_int32(1)
            recv_fun(self.ADeviceHandle, fr_raw, byref(buffersize), self.channel, self.__mode)
            if buffersize.value == 1:
                rx_msg = tosun_convert_msg(fr_raw[0])
                rx_msg.channel = self.channel_info
                return rx_msg, False
        return None, False

    def send(self, msg: RawMessage, timeout: float = 0.1, **kwargs) -> int:
        """
        发送can报文
        """
        sync = kwargs.get("sync", False)
        if self.fd:
            struct = TLibCANFD()
            send_fun = transmit_canfd_sync if sync else transmit_canfd_async
        else:
            struct = TLibCAN()
            send_fun = transmit_can_sync if sync else transmit_can_async
        fr_tx_frame = msg_convert_tosun(struct, msg)
        fr_tx_frame.FIdxChn = self.channel
        args = [self.ADeviceHandle, byref(fr_tx_frame)]
        args.append(timeout * 1000) if sync else args
        ret = send_fun(*args)
        if ret:
            raise ToSunCanOperationError(
                "Failed to send: " + tscan_get_error_description(ret)
            )
        logger.debug(f"Successfully sent:{msg}")
        return ret

    def send_cyclic(self, msg: RawMessage, period) -> int:
        """
        发送周期性的can报文，目前通过注册回调函数修改e2e的方式不好实现，有报错，直接使用和pcan通用的python-can中方法一样可以实现e2e
        """
        if self.fd:
            struct = TLibCANFD()
            send_fun = send_cyclic_canfd_msg
        else:
            struct = TLibCAN()
            send_fun = send_cyclic_can_msg
        fr_tx_frame = msg_convert_tosun(struct, msg)
        fr_tx_frame.FIdxChn = self.channel
        self.send_mags.append(fr_tx_frame)
        ret = send_fun(self.ADeviceHandle, byref(fr_tx_frame), period * 1000)
        return ret

    def flush_rx_buffer(self):
        """
        清空can对应通道的接收缓存
        """
        if self.fd:
            ret = clear_canfd_receive_buffers(self.ADeviceHandle, self.channel)
        else:
            ret = clear_can_receive_buffers(self.ADeviceHandle, self.channel)
        if ret != 0:
            desc = tscan_get_error_description(ret)
            logger.error(f"TSFifo clear can/canfd receive buffers error: {desc}")

    def read_rx_buffer(self) -> int:
        """
        读取can对应通道接收缓存中的报文数量
        """
        count = c_int(0)
        if self.fd:
            read_canfd_rx_buffer_frame_count(self.ADeviceHandle, self.channel, byref(count))
        else:
            read_can_rx_buffer_frame_count(self.ADeviceHandle, self.channel, byref(count))
        return count.value

    def read_tx_buffer(self) -> int:
        """
        读取can对应通道发送缓存中的报文数量
        """
        count = c_int(0)
        read_can_tx_buffer_frame_count(self.ADeviceHandle, self.channel, byref(count))
        return count.value

    def read_buffer(self) -> int:
        """
        读取can对应通道缓存中的报文数量
        """
        count = c_int(0)
        if self.fd:
            read_canfd_buffer_frame_count(self.ADeviceHandle, self.channel, byref(count))
        else:
            read_can_buffer_frame_count(self.ADeviceHandle, self.channel, byref(count))
        return count.value

    def register_event_can(self, on_call_back: typing.Union[OnTx_RxFUNC_CAN, OnTx_RxFUNC_CANFD]):
        """
        register can event
        Triggered when there is message transmission on the bus

        Args:
            on_call_back (OnTx_RxFUNC_can): function

        example:
            def on_can(a_can_msg):
                print(a_can_msg.contents.FData[0])

            on_can_event = OnTx_RxFUNC_can(on_can)
            register_event_can(on_can_event)
        """
        if self.fd:
            ret = register_event_canfd(self.ADeviceHandle, on_call_back)
        else:
            ret = register_event_can(self.ADeviceHandle, on_call_back)
        if ret != 0:
            desc = tscan_get_error_description(ret)
            logger.error(f"TSCAN register event can error: {desc}")
        else:
            logger.info(f"TSCAN register event can successfully.")

    def unregister_event_can(self, on_call_back: OnTx_RxFUNC_CAN):
        """
        注销can发接
        """
        if self.fd:
            ret = unregister_event_canfd(self.ADeviceHandle, on_call_back)
        else:
            ret = unregister_event_can(self.ADeviceHandle, on_call_back)
        if ret != 0:
            desc = tscan_get_error_description(ret)
            logger.error(f"TSCAN unregister event can error: {desc}")
        else:
            logger.debug(f"TSCAN unregister event can successfully.")

    def register_pretx_event_can(self, pre_tx_call_back: typing.Union[OnTx_RxFUNC_CAN, OnTx_RxFUNC_CANFD]):
        """
        register pre tx can event
        Sending a message will trigger and can modify the message data(use transmit_can trigger)

        Args:
            pre_tx_call_back (OnTx_RxFUNC_can): function

        example:
            def pre_can(a_can_msg):
                a_can_msg.contents.FData[0] = 1 #All transmit tx message FData[0] will only be 1
                if a_can_msg.contents.FIdentifier == 1:
                    a_can_msg.contents.FData[0] = 2  #only id=1 can message FData[0] will  be 2

            pre_can_event = OnTx_RxFUNC_can(pre_can)
            register_pretx_event_can(pre_can_event)
        """
        if self.fd:
            ret = register_pretx_event_canfd(self.ADeviceHandle, pre_tx_call_back)
        else:
            ret = register_pretx_event_can(self.ADeviceHandle, pre_tx_call_back)
        if ret != 0:
            desc = tscan_get_error_description(ret)
            logger.error(f"TSCAN register pretx event can error: {desc}")
        else:
            logger.info(f"TSCAN register pretx event can successfully.")

    def unregister_pretx_event_can(self, pre_call_back: OnTx_RxFUNC_CAN):
        """
        # 注销can预发送事件
        """
        if self.fd:
            ret = unregister_pretx_event_canfd(self.ADeviceHandle, pre_call_back)
        else:
            ret = unregister_pretx_event_can(self.ADeviceHandle, pre_call_back)
        if ret != 0:
            desc = tscan_get_error_description(ret)
            logger.error(f"TSCAN unregister pretx event can error: {desc}")
        else:
            logger.debug(f"TSCAN unregister pretx event can successfully.")

    @property
    def can_data(self):
        return self.__can_data

    @can_data.setter
    def can_data(self, value):
        self.__can_data = value

    def on_rx_tx_can(self, a_can_msg):
        """
        用来注册监听总线上所有can报文的事件方法；
        可以根据设定好的过滤条件去发送相应的报文信息
        """
        logger.debug("Enter on rx tx can.")
        can_raw = a_can_msg.contents
        fr_msg = tosun_convert_msg(can_raw)
        logger.debug(f"Listened can raw_message: {fr_msg}")
        filtered_fr_msg = self.callback_recv(fr_msg)
        logger.debug(f"Listened filtered can raw_message: {filtered_fr_msg}")
        if filtered_fr_msg and filtered_fr_msg.channel == self.channel:
            filtered_fr_msg.channel = self.channel_info
            logger.info(f"Listening filtered can raw_message: {filtered_fr_msg}")
            if filtered_fr_msg.is_rx:
                self.received_raw_messages.put(filtered_fr_msg)
            else:
                self.init_counter = False
        logger.debug("Exit on rx tx can.")

    def pre_tx_can(self, Acan):
        """
        用来注册总线上在发送报文之前修改can报文的事件方法；
        当总线发送报文之前会先调用此方法，并对报文数据做些处理后再发送出去
        """
        can_raw = Acan.contents
        can_data = can_raw.FData
        modified_data = self.can_data
        for index in range(min(can_raw.FDLC, len(modified_data))):
            can_data[index] = modified_data[index]
        can_msg = tosun_convert_msg(can_raw)
        logger.info(f"Send can raw_message: {can_msg}")

    def stop(self):
        time.sleep(0.01)
        for msg in self.send_mags:
            if msg.FFDProperties:
                delete_cyclic_send_canfd_msgs(self.ADeviceHandle, byref(msg))
            else:
                delete_cyclic_send_can_msgs(self.ADeviceHandle, byref(msg))
