import argparse
from jidutest_can.script.message_subparser import send_msg, recv_msg


def test_send_message():
    arg = argparse.Namespace(
        interface="smartvci",
        channel=1,
        message_list=["0x202R"], # 0xd013=00:FF:00:00:FF:FF:00:00
        fd=0,
        bitrate=500,
        interval=1000,
        duration=3, 
        debug=1,
        catch_exc=1
    )
    send_msg(arg)


def test_recv_message():
    arg = argparse.Namespace(
        interface="smartvci",
        channel=1,
        id_list=["0x101"], # AI "0xa111" DI "0xd112"
        fd=0,
        bitrate=500,
        duration=10,
        debug=1,
        catch_exc=1
    )
    recv_msg(arg)


if __name__ == "__main__":
    test_send_message()
    # test_recv_message()