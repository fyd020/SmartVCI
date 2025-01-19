1.环境安装


2.使用


2.1命令行使用
查找指令和参数：jidutest-can -h or jidutest-can {子命令} -h
子命令列表：
dbc解析：show-db
显示挂载设备：show-dev
发送原始数据：send-msg
接受原始数据：recv-msg
发送信号报文：send-sgn
接受信号报文：recv-sgn
录报文：log-data
报文回放：replay-data

demo：
显示挂载设备：jidutest-can show-dev
解析dbc：jidutest-can show-db /root/dading/jidutest-can/test_smartvci/resources/DTSDO_C01_B03.dbc
接受2通道原始数据：jidutest-can recv-msg smartvci 2
接受2通道指定id数据：jidutest-can recv-msg smartvci 2 0x101
发送原始数据：jidutest-can send-msg smartvci 1 0xd013=00:FF:00:00:FF:FF:00:00
发送远程帧：jidutest-can send-msg smartvci 1 0x101R

2.2脚本使用

