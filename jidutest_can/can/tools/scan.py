from usb import core
from jidutest_can.can.interfaces.pcan.constants import PCAN_VID
from jidutest_can.can.interfaces.tosun.constants import TOSUN_VID


SUPPORT_VENDORS = {"pcan": PCAN_VID, "tosun": TOSUN_VID}


class ScanCanDevices:

    @staticmethod
    def connected_can_devices() -> dict:
        devices = dict()
        for dev_name, vid in SUPPORT_VENDORS.items():
            devs = core.find(find_all=True, idVendor=vid)
            for dev in devs:
                devices[dev_name] = devices.setdefault(dev_name, [])
                devices[dev_name].append(dev)
        return devices


if __name__ == '__main__':
    can_devices = ScanCanDevices.connected_can_devices()
