import re
import sys
from typing import Dict
from typing import Tuple
from typing import Optional
from jidutest_can.can.tools import Channel


# interface_name => (module, classname)
BACKENDS: Dict[str, Tuple[str, ...]] = {
    "pcan": ("jidutest_can.can.interfaces.pcan", "PcanBus"),
    "socketcan": ("jidutest_can.can.interfaces.socketcan", "SocketcanBus"),
    "virtual": ("jidutest_can.can.interfaces.virtual", "VirtualBus"),
    "tosun": ("jidutest_can.can.interfaces.tosun", "ToSunBus"),
    "smartvci": ("jidutest_can.can.interfaces.smartvci", "SmartVCIBus"),
}

if sys.version_info >= (3, 8):
    from importlib.metadata import entry_points

    entries = entry_points().get("jidutest_can.can.interface", ())
    BACKENDS.update(
        {interface.name: tuple(interface.value.split(":")) for interface in entries}
    )
else:
    from pkg_resources import iter_entry_points

    entries = iter_entry_points("jidutest_can.can.interface")
    BACKENDS.update(
        {
            interface.name: (interface.module_name, interface.attrs[0])
            for interface in entries
        }
    )

VALID_INTERFACES = frozenset(BACKENDS.keys())
CAN_FD_DLC = [0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 16, 20, 24, 32, 48, 64]


def len2dlc(length: int) -> int:
    """Calculate the DLC from data length.

    :param length: Length in number of bytes (0-64)

    :returns: DLC (0-15)
    """
    if length <= 8:
        return length
    for dlc, nof_bytes in enumerate(CAN_FD_DLC):
        if nof_bytes >= length:
            return dlc
    return 15


def dlc2len(dlc: int) -> int:
    """Calculate the data length from DLC.

    :param dlc: DLC (0-15)

    :returns: Data length in number of bytes (0-64)
    """
    return CAN_FD_DLC[dlc] if dlc <= 15 else 64


def channel2int(channel: Optional[Channel]) -> Optional[int]:
    """Try to convert the channel to an integer.

    :param channel:
        Channel string (e.g. `"can0"`, `"CAN1"`) or an integer

    :returns: Channel integer or ``None`` if unsuccessful
    """
    if isinstance(channel, int):
        return channel
    if isinstance(channel, str):
        match = re.match(r".*?(\d+)$", channel)
        if match:
            return int(match.group(1))
    return None
