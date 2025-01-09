# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
import time
import typing

from PySide6.QtCore import QTimer, QUrl, Slot
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QLabel, QMainWindow, QDialog, QPushButton, QHBoxLayout, QDialogButtonBox
from PySide6.QtSerialBus import QCanBus, QCanBusDevice, QCanBusFrame

from connectdialog import ConnectDialog
from busdeviceinfodialog import BusDeviceInfoDialog
from aboutdialog import AboutDialog
from jidutest_can import CanBus, RawMessage
from jidutest_can.can import PCANFD_500000_2000000
from jidutest_can.can.interfaces import BusABC
from ui_mainwindow import Ui_MainWindow
from receivedframesmodel import ReceivedFramesModel


def frame_flags(frame):
    result = " --- "
    if frame.hasBitrateSwitch():
        result[1] = 'B'
    if frame.hasErrorStateIndicator():
        result[2] = 'E'
    if frame.hasLocalEcho():
        result[3] = 'L'
    return result


def show_help():
    url = "https://wiki.jiduauto.com/pages/viewpage.action?pageId=504275976"
    QDesktopServices.openUrl(QUrl(url))


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_ui = Ui_MainWindow()
        self.m_number_frames_written = 0
        self.m_number_frames_received = 0
        self.m_written = None
        self.m_received = None
        self.m_bus: typing.Union[CanBus, BusABC] = None

        self.m_busStatusTimer = QTimer(self)

        self.m_ui.setupUi(self)
        self.m_connect_dialog = ConnectDialog(self)

        self.m_status = QLabel()
        self.m_ui.statusBar.addPermanentWidget(self.m_status)
        self.m_written = QLabel()
        self.m_ui.statusBar.addWidget(self.m_written)
        self.m_received = QLabel()
        self.m_ui.statusBar.addWidget(self.m_received)

        self.m_model = ReceivedFramesModel(self)
        self.m_model.set_queue_limit(1000)
        self.m_ui.receivedFramesView.set_model(self.m_model)

        self.init_actions_connections()
        QTimer.singleShot(50, self.m_connect_dialog.show)

        self.m_appendTimer = QTimer(self)
        self.m_appendTimer.timeout.connect(self.onAppendFramesTimeout)
        self.m_appendTimer.start(350)

    def init_actions_connections(self):
        self.m_ui.actionDisconnect.setEnabled(False)
        self.m_ui.actionDeviceInformation.setEnabled(False)
        self.m_ui.sendFrameBox.setEnabled(False)

        self.m_ui.sendFrameBox.send_frame.connect(self.send_frame)
        self.m_ui.actionConnect.triggered.connect(self._action_connect)
        self.m_connect_dialog.accepted.connect(self.connect_device)
        self.m_ui.actionDisconnect.triggered.connect(self.disconnect_device)
        self.m_ui.actionResetController.triggered.connect(self._reset_controller)
        self.m_ui.actionQuit.triggered.connect(self.close)
        self.m_ui.actionAboutJiDUSignal.triggered.connect(self.about)
        self.m_ui.actionClearLog.triggered.connect(self.m_model.clear)
        self.m_ui.actionPluginDocumentation.triggered.connect(show_help)
        self.m_ui.actionDeviceInformation.triggered.connect(self._action_device_information)

    @Slot()
    def _action_connect(self):
        if self.m_bus:
            self.m_bus = None
        self.m_connect_dialog.show()

    @Slot()
    def _reset_controller(self):
        self.m_bus.reset()

    @Slot()
    def _action_device_information(self):
        info = self.m_bus.deviceInfo()
        dialog = BusDeviceInfoDialog(info, self)
        dialog.exec()

    # @Slot(QCanBusDevice.CanBusError)
    # def process_errors(self, error):
    #     if error != QCanBusDevice.NoError:
    #         self.m_status.setText(self.m_bus.errorString())

    @Slot()
    def connect_device(self):
        p = self.m_connect_dialog.settings()
        if p.use_model_ring_buffer:
            self.m_model.set_queue_limit(p.model_ring_buffer_size)
        else:
            self.m_model.set_queue_limit(0)
        try:
            bus = CanBus(interface=p.plugin_name, channel=p.device_interface_name, fd=p.configurations.get("fd"), **PCANFD_500000_2000000)
        except Exception as ex:
            self.m_status.setText(f"Error connecting device '{p.plugin_name}', reason: '{ex}'")
            return

        self.m_number_frames_written = 0
        self.m_bus = bus
        # self.m_bus.errorOccurred.connect(self.process_errors)
        # self.m_bus.framesReceived.connect(self.process_received_frames)
        # self.m_bus.framesWritten.connect(self.process_frames_written)

        # if p.use_configuration_enabled:
        #     for k, v in p.configurations:
        #         self.m_bus.setConfigurationParameter(k, v)

        # if not self.m_bus.connectDevice():
        #     e = self.m_bus.errorString()
        #     self.m_status.setText(f"Connection error: {e}")
        #     self.m_bus = None
        # else:
        self.m_ui.actionConnect.setEnabled(False)
        self.m_ui.actionDisconnect.setEnabled(True)
        self.m_ui.actionDeviceInformation.setEnabled(True)
        self.m_ui.sendFrameBox.setEnabled(True)
        bit_rate = PCANFD_500000_2000000.nom_bitrate / 1000
        if bus.fd:
            data_bit_rate = PCANFD_500000_2000000.data_bitrate / 1000
            m = f"Plugin: {p.plugin_name}, connected to {p.device_interface_name} at {bit_rate} / {data_bit_rate} kBit/s"
            self.m_status.setText(m)
        else:
            m = f"Plugin: {p.plugin_name}, connected to {p.device_interface_name} at {bit_rate} kBit/s"
            self.m_status.setText(m)

        if self.m_bus.state:
            self.m_busStatusTimer.start(2000)
        else:
            self.m_ui.busStatus.setText("No CAN bus status available.")

    @Slot()
    def disconnect_device(self):
        if not self.m_bus:
            return
        self.m_busStatusTimer.stop()
        self.m_bus.shutdown()
        self.m_ui.actionConnect.setEnabled(True)
        self.m_ui.actionDisconnect.setEnabled(False)
        self.m_ui.actionDeviceInformation.setEnabled(False)
        self.m_ui.sendFrameBox.setEnabled(False)
        self.m_status.setText("Disconnected")

    @Slot(int)
    def process_frames_written(self, count):
        self.m_number_frames_written += count
        self.m_written.setText(f"{self.m_number_frames_written} frames written")

    def closeEvent(self, event):
        self.m_connect_dialog.close()
        event.accept()

    @Slot()
    def process_received_frames(self):
        if not self.m_bus:
            return
        while self.m_bus:
            self.m_number_frames_received += 1
            frame: RawMessage = self.m_bus.recv(1)
            # data = ""
            # if frame.is_error_frame:
            #     data = self.m_bus.interpretErrorFrame(frame)
            # else:
            #     data = frame.payload().toHex(' ').toUpper()
            #
            # secs = frame.timeStamp().seconds()
            # microsecs = frame.timeStamp().microSeconds() / 100
            # time = f"{secs:>10}.{microsecs:0>4}"
            # flags = frame_flags(frame)
            #
            # id = f"{frame.frameId():x}"
            # dlc = f"{frame.payload().size()}"
            # frame = [f"{self.m_number_frames_received}", time, flags, id, dlc, data]
            self.m_model.append_frame(frame)

    @Slot(RawMessage)
    def send_frame(self, frame):
        if self.m_bus:
            frame.channel = self.m_bus.channel_info
            self.m_bus.send(frame)

    @Slot()
    def onAppendFramesTimeout(self):
        if not self.m_bus:
            return
        if self.m_model.need_update():
            self.m_model.update()
            if self.m_connect_dialog.settings().use_autoscroll:
                self.m_ui.receivedFramesView.scrollToBottom()
            self.m_received.setText(f"{self.m_number_frames_received} frames received")

    @Slot()
    def about(self):
        dialog = AboutDialog(self)
        dialog.exec()
