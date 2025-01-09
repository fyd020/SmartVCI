from jidutest_can.can.tools.bit_timing import BitTimingFd


PCANFD_500000_2000000 = BitTimingFd(80000000, 10, 12, 3, 1, 4, 7, 2, 1)
PCANFD_500000_5000000 = BitTimingFd(80000000, 10, 12, 3, 1, 2, 5, 2, 1)
PCAN_VID = 0x0c72
