# -*- coding: utf-8 -*-
"""
@File        : define_tosun.py
@Author      : pengtao.li@jiduauto.com
@Time        : 2023/6/1 11:11
@Update Time :
@Description : tosun dll/so definition file

"""
import os
import logging
import platform
from ctypes import *
from jidutest_can.package import libc_path
from jidutest_can.can.message import RawMessage
from jidutest_can.can.interfaces.tosun.constants import ERROR_CODE


_curr_working_abs_path = os.path.abspath(os.curdir)
_arch, _os2 = platform.architecture()
_os = platform.system()
logger = logging.getLogger(__file__)
_is_windows, _is_linux = False, False
if 'windows' in _os.lower():
    _is_windows = True
    if _arch == '32bit':
        _lib_path = libc_path / 'libtosun' / 'windows' / 'x86' / 'libTSCAN.dll'
    else:
        _lib_path = libc_path / 'libtosun' / 'windows' / 'x64' / 'libTSCAN.dll'
    dll = windll.LoadLibrary(str(_lib_path))
elif 'linux' in _os.lower():
    _is_linux = True
    if _arch == '64bit':
        _linux_lib_dir = libc_path / 'libtosun' / 'linux'
        os.chdir(str(_linux_lib_dir))
        _lib_path = os.path.join(_linux_lib_dir / 'libTSCANApiOnLinux.so')
    else:
        _lib_path = None
    if _lib_path:
        dll = cdll.LoadLibrary(str(_lib_path))
else:
    _library = None
os.chdir(_curr_working_abs_path)


class READ_TX_RX_DEF:
    """
    TX_RX_MESSAGES:receive msg inclued tx and rx msg
    ONLY_RX_MESSAGES: only receive rx msg
    """
    ONLY_RX_MESSAGES = c_uint8(0)
    TX_RX_MESSAGES = c_uint8(1)


class TLIBCANFDControllerType:
    """
    set canfd baudrate and canfd mode : can isocanfd non-isocanfd
    function:
    tsapp_configure_baudrate_canfd
    """
    lfdtCAN = c_int(0)
    lfdtISOCAN = c_int(1)
    lfdtNonISOCAN = c_int(2)


class TLIBCANFDControllerMode:
    """
    set canfd Controller Mode :Normal ACKoff Restricted
    function:
    tsapp_configure_baudrate_canfd
    """
    lfdmNormal = c_int(0)
    lfdmACKOff = c_int(1)
    lfdmRestricted = c_int(2)


DLC_DATA_BYTE_CNT = (
    0, 1, 2, 3, 4, 5, 6, 7,
    8, 12, 16, 20, 24, 32, 48, 64
)


class A120:
    """
    set hardware termination resistor
    function:
    tsapp_configure_baudrate_canfd
    """
    DEABLEA120 = c_int(0)
    ENABLEA120 = c_int(1)


class TLibCAN(Structure):
    _pack_ = 1
    _fields_ = [
        ("FIdxChn", c_uint8),
        ("FProperties", c_uint8),  # 定义can数据类型  1:标准数据帄1 7 3:标准远程帄1 7 5：扩展数据帧 7：扩展远程帧
        ("FDLC", c_uint8),
        ("FReserved", c_uint8),
        ("FIdentifier", c_int32),
        ("FTimeUs", c_uint64),
        ("FData", c_uint8 * 8),
    ]


class TLibCANFD(Structure):
    _pack_ = 1
    _fields_ = [
        ("FIdxChn", c_uint8),
        ("FProperties", c_uint8),  # 定义canfd数据类型  1:FD标准帄1 7 5:FD扩展帄1 7
        ("FDLC", c_uint8),
        ("FFDProperties", c_uint8),  # 0:普  can数据帄1 7 1：canfd数据帄1 7
        ("FIdentifier", c_int32),
        ("FTimeUs", c_ulonglong),
        ("FData", c_ubyte * 64),
    ]


def tscan_get_error_description(ACode: int):
    # linux下此方法报核心段错误
    errorcode = POINTER(POINTER(c_char))()
    if ACode == 0:
        return "确定"
    else:
        if 'linux' in _os.lower():
            return ERROR_CODE.get(ACode, ACode)
        else:
            r = dll.tscan_get_error_description(c_int32(ACode), byref(errorcode))
            if r == 0:
                ADesc = string_at(errorcode).decode("utf-8")
                return ADesc
            else:
                return r


def tscan_get_can_channel_count(AHandle):
    if _is_linux:
        logger.warning(f"There is no 'tscan_get_can_channel_count' method under Linux system，"
                       f"and the default connected TOSUN device are 2 can channel.")
        return 2
    ACount = c_int32(0)
    dll.tscan_get_can_channel_count(AHandle, byref(ACount))
    return ACount.value


def tosun_convert_msg(msg) -> RawMessage:
    """
    TLIBCAN  TLIBCANFD msg convert to can.Message
    Easy python-can to use
    """
    if isinstance(msg, TLibCAN):
        dlc = msg.FDLC
        return RawMessage(
            timestamp=float(msg.FTimeUs) / 1000000,
            arbitration_id=msg.FIdentifier,
            is_extended_id=msg.FProperties & 0x04,
            is_remote_frame=msg.FProperties & 0x02,
            is_error_frame=msg.FProperties & 0x80,
            channel=msg.FIdxChn,
            dlc=dlc,
            data=bytes(msg.FData[:dlc]),
            is_fd=False,
            is_rx=False if msg.FProperties & 0x01 else True,
        )
    elif isinstance(msg, TLibCANFD):
        dlc = DLC_DATA_BYTE_CNT[msg.FDLC]
        return RawMessage(
            timestamp=float(msg.FTimeUs) / 1000000,
            arbitration_id=msg.FIdentifier,
            is_extended_id=msg.FProperties & 0x04,
            is_remote_frame=msg.FProperties & 0x02,
            channel=msg.FIdxChn,
            dlc=dlc,
            data=bytes(msg.FData[:dlc]),
            is_fd=msg.FFDProperties & 0x01,
            is_rx=False if msg.FProperties & 0x01 else True,
            bitrate_switch=msg.FFDProperties & 0x02,
            error_state_indicator=msg.FFDProperties & 0x04,
            is_error_frame=msg.FProperties & 0x80
        )
    elif isinstance(msg, RawMessage):
        return msg
    else:
        raise ArgumentError(f'Unknown message type: {type(msg)}')


def msg_convert_tosun(struct, msg):
    """
    can.Message convert to  TLIBCAN  TLIBCANFD msg
    Easy python-can to use
    """
    if msg.is_fd:
        struct.FFDProperties = 0x01 | (0x02 if msg.bitrate_switch else 0x00) | (
            0x04 if msg.error_state_indicator else 0x00)
    struct.FProperties = 0x01 | (0x00 if msg.is_rx else 0x01) | (
        0x02 if msg.is_remote_frame else 0x00) | (0x04 if msg.is_extended_id else 0x00)
    try:
        struct.FDLC = DLC_DATA_BYTE_CNT.index(msg.dlc)
    except:
        if msg.dlc < 0x10:
            struct.FDLC = msg.dlc
        else:
            raise ArgumentError("Message DLC input error")

    struct.FIdentifier = msg.arbitration_id
    struct.FTimeUs = int(msg.timestamp)
    for index, item in enumerate(msg.data):
        struct.FData[index] = item
    return struct


finalize_lib_tscan = dll.finalize_lib_tscan

initialize_lib_tsmaster = dll.initialize_lib_tscan
initialize_lib_tsmaster.argtypes = [
    c_bool,
    c_bool,
    c_bool,
]

tscan_connect = dll.tscan_connect
tscan_connect.argtypes = [
    c_char_p,
    POINTER(c_size_t),
]
tscan_connect.restype = c_uint32

tscan_scan_devices = dll.tscan_scan_devices
tscan_scan_devices.argtypes = [
    POINTER(c_uint32),
]
tscan_scan_devices.restype = c_uint32

tscan_get_device_info = dll.tscan_get_device_info
tscan_get_device_info.argtypes = [
    c_uint64,
    POINTER(POINTER(c_char_p)),
    POINTER(POINTER(c_char_p)),
    POINTER(POINTER(c_char_p)),
]
tscan_get_device_info.restype = c_uint32

tscan_disconnect_by_handle = dll.tscan_disconnect_by_handle
tscan_disconnect_by_handle.argtypes = [
    c_size_t,
]
tscan_disconnect_by_handle.restype = c_uint32

tscan_disconnect_all_devices = dll.tscan_disconnect_all_devices
tscan_disconnect_all_devices.restype = c_uint32

configure_canfd_baudrate = dll.tscan_config_canfd_by_baudrate
configure_canfd_baudrate.argtypes = [
    c_size_t,
    c_int,
    c_double,
    c_double,
    c_int,
    c_int,
    c_bool,
]
configure_canfd_baudrate.restype = c_uint32

configure_can_baudrate = dll.tscan_config_can_by_baudrate
configure_can_baudrate.argtypes = [
    c_size_t,
    c_int,
    c_double,
    c_int,
]
configure_can_baudrate.restype = c_uint32

if _is_windows:
    # linux下面没有此方法
    configure_canfd_regs = dll.tscan_configure_canfd_regs
    configure_canfd_regs.argtypes = [
        c_size_t,
        c_int,
        c_double,
        c_uint32,
        c_uint32,
        c_uint32,
        c_uint32,
        c_double,
        c_uint32,
        c_uint32,
        c_uint32,
        c_uint32,
        c_int,
        c_int,
        c_bool
    ]
    configure_canfd_regs.restype = c_uint32
    
    configure_can_regs = dll.tscan_configure_can_regs
    configure_can_regs.argtypes = [
        c_size_t,
        c_int,
        c_double,
        c_uint32,
        c_uint32,
        c_uint32,
        c_uint32,
        c_uint32,
        c_bool
    ]
    configure_can_regs.restype = c_uint32

send_cyclic_canfd_msg = dll.tscan_add_cyclic_msg_canfd
send_cyclic_canfd_msg.argtypes = [
    c_size_t,
    POINTER(TLibCANFD),
    c_float,
]
send_cyclic_canfd_msg.restype = c_uint32

send_cyclic_can_msg = dll.tscan_add_cyclic_msg_can
send_cyclic_can_msg.argtypes = [
    c_size_t,
    POINTER(TLibCAN),
    c_float,
]
send_cyclic_can_msg.restype = c_uint32

transmit_can_async = dll.tscan_transmit_can_async
transmit_can_async.argtypes = [
    c_size_t,
    POINTER(TLibCAN),
]
transmit_can_async.restype = c_uint32

transmit_can_sync = dll.tscan_transmit_can_sync
transmit_can_sync.argtypes = [
    c_size_t,
    POINTER(TLibCAN),
    c_float,
]
transmit_can_sync.restype = c_uint32

transmit_canfd_async = dll.tscan_transmit_canfd_async
transmit_canfd_async.argtypes = [
    c_size_t,
    POINTER(TLibCANFD),
]
transmit_canfd_async.restype = c_uint32

transmit_canfd_sync = dll.tscan_transmit_canfd_sync
transmit_canfd_sync.argtypes = [
    c_size_t,
    POINTER(TLibCANFD),
    c_float,
]
transmit_canfd_sync.restype = c_uint32

delete_cyclic_send_canfd_msgs = dll.tscan_delete_cyclic_msg_canfd
delete_cyclic_send_canfd_msgs.argtypes = [
    c_size_t,
    POINTER(TLibCANFD),
]
delete_cyclic_send_canfd_msgs.restype = c_uint32

delete_cyclic_send_can_msgs = dll.tscan_delete_cyclic_msg_can
delete_cyclic_send_can_msgs.argtypes = [
    c_size_t,
    POINTER(TLibCAN),
]
delete_cyclic_send_can_msgs.restype = c_uint32

receive_can_msgs = dll.tsfifo_receive_can_msgs
receive_can_msgs.argtypes = [
    c_size_t,
    Array,
    POINTER(c_int32),
    c_uint32,
    c_uint8,
]
receive_can_msgs.restype = c_uint32

receive_canfd_msgs = dll.tsfifo_receive_canfd_msgs
receive_canfd_msgs.argtypes = [
    c_size_t,
    Array,
    POINTER(c_int32),
    c_uint32,
    c_uint8,
]
receive_canfd_msgs.restype = c_uint32

clear_can_receive_buffers = dll.tsfifo_clear_can_receive_buffers
clear_can_receive_buffers.argtypes = [
    c_size_t,
    c_int32,
]
clear_can_receive_buffers.restype = c_uint32

clear_canfd_receive_buffers = dll.tsfifo_clear_canfd_receive_buffers
clear_canfd_receive_buffers.argtypes = [
    c_size_t,
    c_int32,
]
clear_canfd_receive_buffers.restype = c_uint32

read_can_buffer_frame_count = dll.tsfifo_read_can_buffer_frame_count
read_can_buffer_frame_count.argtypes = [
    c_size_t,
    c_int,
    POINTER(c_int),
]
read_can_buffer_frame_count.restype = c_uint32

read_canfd_buffer_frame_count = dll.tsfifo_read_canfd_buffer_frame_count
read_canfd_buffer_frame_count.argtypes = [
    c_size_t,
    c_int,
    POINTER(c_int),
]
read_canfd_buffer_frame_count.restype = c_uint32

read_can_tx_buffer_frame_count = dll.tsfifo_read_can_tx_buffer_frame_count
read_can_tx_buffer_frame_count.argtypes = [
    c_size_t,
    c_int,
    POINTER(c_int),
]
read_can_tx_buffer_frame_count.restype = c_uint32

read_can_rx_buffer_frame_count = dll.tsfifo_read_can_rx_buffer_frame_count
read_can_rx_buffer_frame_count.argtypes = [
    c_size_t,
    c_int,
    POINTER(c_int),
]
read_can_rx_buffer_frame_count.restype = c_uint32

read_canfd_rx_buffer_frame_count = dll.tsfifo_read_canfd_rx_buffer_frame_count
read_canfd_rx_buffer_frame_count.argtypes = [
    c_size_t,
    c_int,
    POINTER(c_int),
]
read_canfd_rx_buffer_frame_count.restype = c_uint32

# 回调事件
PCAN = POINTER(TLibCAN)
if _is_windows:
    OnTx_RxFUNC_CAN = WINFUNCTYPE(None, PCAN)
else:
    OnTx_RxFUNC_CAN = CFUNCTYPE(None, PCAN)

PCANFD = POINTER(TLibCANFD)
if _is_windows:
    OnTx_RxFUNC_CANFD = WINFUNCTYPE(None, PCANFD)
else:
    OnTx_RxFUNC_CANFD = CFUNCTYPE(None, PCANFD)

register_event_can = dll.tscan_register_event_can
register_event_can.argtypes = [
    c_size_t,
    OnTx_RxFUNC_CAN,
]
register_event_can.restype = c_uint32

unregister_event_can = dll.tscan_unregister_event_can
unregister_event_can.argtypes = [
    c_size_t,
    OnTx_RxFUNC_CAN,
]
unregister_event_can.restype = c_uint32

register_pretx_event_can = dll.tscan_register_pretx_event_can
register_pretx_event_can.argtypes = [
    c_size_t,
    OnTx_RxFUNC_CAN,
]
register_pretx_event_can.restype = c_uint32

unregister_pretx_event_can = dll.tscan_unregister_pretx_event_can
unregister_pretx_event_can.argtypes = [
    c_size_t,
    OnTx_RxFUNC_CAN,
]
unregister_pretx_event_can.restype = c_uint32

register_event_canfd = dll.tscan_register_event_canfd
register_event_canfd.argtypes = [
    c_size_t,
    OnTx_RxFUNC_CANFD,
]
register_event_canfd.restype = c_uint32

unregister_event_canfd = dll.tscan_unregister_event_canfd
unregister_event_canfd.argtypes = [
    c_size_t,
    OnTx_RxFUNC_CANFD,
]
unregister_event_canfd.restype = c_uint32

register_pretx_event_canfd = dll.tscan_register_pretx_event_canfd
register_pretx_event_canfd.argtypes = [
    c_size_t,
    OnTx_RxFUNC_CANFD,
]
register_pretx_event_canfd.restype = c_uint32

unregister_pretx_event_canfd = dll.tscan_unregister_pretx_event_canfd
unregister_pretx_event_canfd.argtypes = [
    c_size_t,
    OnTx_RxFUNC_CANFD,
]
unregister_pretx_event_canfd.restype = c_uint32
