====================
jidutest_can使用教程
====================
- 准备环境：

  + 准备硬件设备
  
   目前只支持PCAN， 后续会持续支持图莫斯和同星
  
  + 安装Python解释器，3.8以上版本：

   python -V

  + 创建虚拟环境：
     
   python -m venv env

  + 激活虚拟环境：
  
   【Windows】env\Scripts\activate.bat
    
   【Linux  】source env/bin/activate

  + 升级pip和setuptools到最新版本：
  
   python -m pip install -U pip setuptools

   pip list -v

  + 获取jidutest-can包的特定版本：

   git clone hhttps://github.com/fyd020/SmartVCI.git

  + 安装本包的依赖及其本身：
  
   【本包使用者】pip install SmartVCI/

   【本包开发者】pip install -e SmartVCI/

  + 删除下载包：

   【Windows】rmdir /s SmartVCI/

   【Linux  】rm -rf SmartVCI/

- 命令行操作：

  + 查看命令行帮助信息：

   jidutest-can -h

  + 查看本包的版本信息：
  
   jidutest-can version
  
  + 查看CAN卡列表和信息（目前只支持Linux平台）：
  
   jidutest-can show-dev

  + 查看CAN数据库文件信息（目前测试过DBC格式；支持查看整个文件，可以过滤特定的消息和信号）：

   jidutest-can show-db SDB22R01_BGM_ADCANFD_220218_PreRelease.dbc

   jidutest-can show-db SDB22R01_BGM_ADCANFD_220218_PreRelease.dbc 0x120

   jidutest-can show-db SDB22R01_BGM_ADCANFD_220218_PreRelease.dbc BgmADCANFDFr05

   jidutest-can show-db SDB22R01_BGM_ADCANFD_220218_PreRelease.dbc PNC40_BGM

   jidutest-can show-db SDB22R01_BGM_ADCANFD_220218_PreRelease.dbc BgmADCANFDFr05 PNC40_BGM 0x120

  + 发送裸数据（支持CAN和CANFD）：
  
   jidutest-can send-msg --fd 0 pcan 1 0x123=11:22:33:44:55:66:77:88

   jidutest-can send-msg --fd 1 pcan 1 0x123=11:22:33:44:55:66:77:88

   jidutest-can send-msg --fd 1 pcan 1 0x123=11:22:33:44:55:66:77:88 0x12345=88:77:66:55:44:33:22:11
   
  + 接收裸数据（支持CAN和CANFD，支持只接收指定FrameID的数据）：

   jidutest-can recv-msg --fd 1 pcan 2

   jidutest-can recv-msg --fd 1 pcan 2 0x123

   jidutest-can recv-msg --fd 1 pcan 2 0x123 0x234

  + 发送信号（支持一次发送单个/多个信号）：

   jidutest-can send-sgn pcan 1 SDB22R04_BGM_BodyCAN_220923_Release.dbc WinOpenDrvrReq=26

   jidutest-can send-sgn pcan 1 SDB22R04_BGM_BodyCAN_220923_Release.dbc WinOpenDrvrReq=WinAndRoofAndCurtPosnTyp_OpenFull

   jidutest-can send-sgn pcan 1 SDB22R04_BGM_BodyCAN_220923_Release.dbc WinOpenDrvrReq=26 WinOpenPassReq=WinAndRoofAndCurtPosnTyp_OpenFull

   jidutest-can send-sgn pcan 1 SDB22R04_BGM_BodyCAN_220923_Release.dbc WinOpenDrvrReq=26 DoorOpenwarnLeIndcn=LcmaIndcn_LcmaWarnLvl1

  + 接收信号（支持接收一个/多个信号）：

   jidutest-can recv-sgn pcan 2 SDB22R04_BGM_BodyCAN_220923_Release.dbc WinOpenDrvrReq

   jidutest-can recv-sgn pcan 2 SDB22R04_BGM_BodyCAN_220923_Release.dbc WinOpenDrvrReq DoorOpenwarnLeIndcn

  + 记录报文（支持blf，asc，csv等格式, 如demo.blf, demo.asc, demo.csv）：

   jidutest-can log-data pcan 1 <file name>

  + 回放报文（支持blf，asc，csv等格式, 如demo.blf, demo.asc, demo.csv）：

   jidutest-can replay-data pcan 1 <file name>

  + 转换报文格式（支持blf，asc，csv等格式, 如demo.blf, demo.asc, demo.csv）：

   jidutest-can log-convert source_file dest_file

  + 通过dbc解析报文数据：

   jidutest-can log-parse log_file db_path [dest_file]

  + 子命令更多参数帮助信息可使用：

   jidutest-can <子命令> -h

- 测试用例demo文件（可参考sample文件夹下的测试用例进行测试）

  + 配置文件
  
   pyproject.toml
   
  + 自定义Controller来接收报文

   python sample_receive_messages.py

   python sample_receive_message_once.py
   
  + 自定义Controller来发送报文

   python sample_send_messages.py
   
   python sample_send_messages_once.py
   
  + 自定义Controller来接收信号

   python sample_receive_signals.py
   
   python sample_receive_signals_once.py

  + 自定义Controller来发送信号

   python sample_send_signals.py

   python sample_send_signals_once.py

  + 自定义Bus来录制报文

   python sample_log_data.py

  + 自定义Bus来打印报文

   python sample_print_data.py

  + 自定义Bus来回放报文

   python sample_replay_data.py

  + 目录结构

   sample
     ├── __init__.py

     ├── pyproject.toml

     ├── sample_log_data.py

     ├── sample_print_data.py

     ├── sample_replay_data.py

     ├── sample_receive_messages.py

     ├── sample_receive_message_once.py

     ├── sample_send_messages.py

     ├── sample_send_messages_once.py

     ├── sample_receive_signals.py

     ├── sample_receive_signals_once.py

     ├── sample_send_signals.py

     └── sample_send_signals_once.py

Smartvci脚本执行：
python3 test/test_smartvci/card_control_di.py  # 执行di版卡操作
python3 test/test_smartvci/card_control_do.py  # 执行do版卡操作
python3 test/test_smartvci/card_control_ai.py  # 执行ai版卡操作
