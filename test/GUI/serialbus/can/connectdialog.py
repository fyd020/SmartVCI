# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtCore import QSettings, Qt, Slot
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QDialog
from jidutest_can.can import CanBus
from jidutest_can.can import CanInitializationError
from jidutest_can.can.tools.scan import ScanCanDevices
from ui_connectdialog import Ui_ConnectDialog


class Settings:
    def __init__(self):
        self.plugin_name = ""
        self.device_interface_name = ""
        self.configurations = dict()
        self.use_configuration_enabled = False
        self.use_model_ring_buffer = True
        self.model_ring_buffer_size = 1000
        self.use_autoscroll = False


class ConnectDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_ui = Ui_ConnectDialog()
        self.m_currentSettings = Settings()
        self.m_channels = []
        self.m_settings = QSettings("JiDUProject", "JiDU Signal")
        self.m_ui.setupUi(self)

        self.m_ui.errorFilterEdit.setValidator(QIntValidator(0, 0x1FFFFFFF, self))

        # self.m_ui.loopbackBox.addItem("unspecified")
        # self.m_ui.loopbackBox.addItem("False", False)
        # self.m_ui.loopbackBox.addItem("True", True)
        #
        # self.m_ui.receiveOwnBox.addItem("unspecified")
        # self.m_ui.receiveOwnBox.addItem("False", False)
        # self.m_ui.receiveOwnBox.addItem("True", True)

        self.m_ui.canFdBox.addItem("False", False)
        self.m_ui.canFdBox.addItem("True", True)

        self.m_ui.dataBitrateBox.set_flexible_date_rate_enabled(True)

        self.m_ui.okButton.clicked.connect(self.ok)
        self.m_ui.cancelButton.clicked.connect(self.cancel)
        self.m_ui.useConfigurationBox.toggled.connect(self.m_ui.configurationBox.setEnabled)
        self.m_ui.pluginListBox.currentTextChanged.connect(self.plugin_changed)
        self.m_ui.interfaceListBox.currentTextChanged.connect(self.interface_changed)
        self.m_ui.ringBufferBox.stateChanged.connect(self._ring_buffer_changed)

        self.m_ui.rawFilterEdit.hide()
        self.m_ui.rawFilterLabel.hide()

        self.devices = ScanCanDevices.connected_can_devices()
        self.m_ui.pluginListBox.addItems(self.devices.keys())

        self.restore_settings()

    @Slot(int)
    def _ring_buffer_changed(self, state):
        self.m_ui.ringBufferLimitBox.setEnabled(state == Qt.CheckState.Checked.value)

    def settings(self):
        return self.m_currentSettings

    def save_settings(self):
        qs = self.m_settings
        cur = self.m_currentSettings
        qs.beginGroup("LastSettings")
        qs.setValue("PluginName", self.m_currentSettings.plugin_name)
        qs.setValue("DeviceInterfaceName", cur.device_interface_name)
        qs.setValue("UseAutoscroll", cur.use_autoscroll)
        qs.setValue("UseRingBuffer", cur.use_model_ring_buffer)
        qs.setValue("RingBufferSize", cur.model_ring_buffer_size)
        qs.setValue("UseCustomConfiguration", cur.use_configuration_enabled)

        # if cur.use_configuration_enabled:
        #     qs.setValue("Loopback",
        #                 self.configuration_value(QCanBusDevice.LoopbackKey))
        #     qs.setValue("ReceiveOwn",
        #                 self.configuration_value(QCanBusDevice.ReceiveOwnKey))
        #     qs.setValue("ErrorFilter",
        #                 self.configuration_value(QCanBusDevice.ErrorFilterKey))
        #     qs.setValue("BitRate",
        #                 self.configuration_value(QCanBusDevice.BitRateKey))
        #     qs.setValue("CanFd",
        #                 self.configuration_value(QCanBusDevice.CanFdKey))
        #     qs.setValue("DataBitRate",
        #                 self.configuration_value(QCanBusDevice.DataBitRateKey))
        qs.endGroup()

    def restore_settings(self):
        qs = self.m_settings
        cur = self.m_currentSettings
        qs.beginGroup("LastSettings")
        cur.plugin_name = qs.value("PluginName", "", str)
        cur.device_interface_name = qs.value("DeviceInterfaceName", "", str)
        cur.use_autoscroll = qs.value("UseAutoscroll", False, bool)
        cur.use_model_ring_buffer = qs.value("UseRingBuffer", False, bool)
        cur.model_ring_buffer_size = qs.value("RingBufferSize", 0, int)
        cur.use_configuration_enabled = qs.value("UseCustomConfiguration", False, bool)

        self.revert_settings()

        if cur.use_configuration_enabled:
            self.m_ui.loopbackBox.setCurrentText(qs.value("Loopback"))
            self.m_ui.receiveOwnBox.setCurrentText(qs.value("ReceiveOwn"))
            self.m_ui.errorFilterEdit.setText(qs.value("ErrorFilter"))
            self.m_ui.bitrateBox.setCurrentText(qs.value("BitRate"))
            self.m_ui.canFdBox.setCurrentText(qs.value("CanFd"))
            self.m_ui.dataBitrateBox.setCurrentText(qs.value("DataBitRate"))

        qs.endGroup()
        self.update_settings()

    @Slot(str)
    def plugin_changed(self, plugin):
        self.m_ui.interfaceListBox.clear()
        try:
            bus = CanBus(interface=plugin, channel=1)
        except CanInitializationError as ex:
            print(ex)
            return
        bus.shutdown()
        self.m_channels = list()
        if bus.channel_info.startswith("TOSUN_CAN"):
            for i in bus.device_info:
                self.m_channels.extend([str(channel) for channel in i[3]])
        else:
            self.m_channels.append(str(1))
            for channel in range(2, 19):
                try:
                    bus = CanBus(interface=plugin, channel=channel)
                except CanInitializationError as ex:
                    break
                bus.shutdown()
                self.m_channels.append(str(channel))
        for channel in self.m_channels:
            self.m_ui.interfaceListBox.addItem(channel)

    @Slot(str)
    def interface_changed(self, channel):
        self.m_ui.deviceInfoBox.set_device_info(channel)
        self.m_ui.deviceInfoBox.clear()

    @Slot()
    def ok(self):
        self.update_settings()
        self.save_settings()
        self.accept()

    @Slot()
    def cancel(self):
        self.revert_settings()
        self.reject()

    def configuration_value(self, key):
        result = None
        for k, v in self.m_currentSettings.configurations.items():
            if k == key:
                result = v
                break
        return str(result)

    def revert_settings(self):
        self.m_ui.pluginListBox.setCurrentText(self.m_currentSettings.plugin_name)
        self.m_ui.interfaceListBox.setCurrentText(self.m_currentSettings.device_interface_name)
        self.m_ui.useConfigurationBox.setChecked(self.m_currentSettings.use_configuration_enabled)

        self.m_ui.ringBufferBox.setChecked(self.m_currentSettings.use_model_ring_buffer)
        self.m_ui.ringBufferLimitBox.setValue(self.m_currentSettings.model_ring_buffer_size)
        self.m_ui.autoscrollBox.setChecked(self.m_currentSettings.use_autoscroll)

        # value = self.configuration_value(QCanBusDevice.LoopbackKey)
        # self.m_ui.loopbackBox.setCurrentText(value)
        #
        # value = self.configuration_value(QCanBusDevice.ReceiveOwnKey)
        # self.m_ui.receiveOwnBox.setCurrentText(value)
        #
        # value = self.configuration_value(QCanBusDevice.ErrorFilterKey)
        # self.m_ui.errorFilterEdit.setText(value)
        #
        # value = self.configuration_value(QCanBusDevice.BitRateKey)
        # self.m_ui.bitrateBox.setCurrentText(value)
        #
        # value = self.configuration_value(QCanBusDevice.CanFdKey)
        # self.m_ui.canFdBox.setCurrentText(value)
        #
        # value = self.configuration_value(QCanBusDevice.DataBitRateKey)
        # self.m_ui.dataBitrateBox.setCurrentText(value)

    def update_settings(self):
        self.m_currentSettings.plugin_name = self.m_ui.pluginListBox.currentText()
        self.m_currentSettings.device_interface_name = self.m_ui.interfaceListBox.currentText()
        self.m_currentSettings.use_configuration_enabled = self.m_ui.useConfigurationBox.isChecked()

        self.m_currentSettings.use_model_ring_buffer = self.m_ui.ringBufferBox.isChecked()
        self.m_currentSettings.model_ring_buffer_size = self.m_ui.ringBufferLimitBox.value()
        self.m_currentSettings.use_autoscroll = self.m_ui.autoscrollBox.isChecked()

        if self.m_currentSettings.use_configuration_enabled:
            self.m_currentSettings.configurations.clear()
            # process LoopBack
            if self.m_ui.loopbackBox.currentIndex() != 0:
                self.m_currentSettings.configurations["loopback_box"] = self.m_ui.loopbackBox.currentData()

            # process ReceiveOwnKey
            if self.m_ui.receiveOwnBox.currentIndex() != 0:
                self.m_currentSettings.configurations["receive_own_box"] = self.m_ui.receiveOwnBox.currentData()

            # process error filter
            error_filter = self.m_ui.errorFilterEdit.text()
            if error_filter:
                ok = False
                try:
                    int(error_filter)  # check if value contains a valid integer
                    ok = True
                except ValueError:
                    pass
                if ok:
                    self.m_currentSettings.configurations["error_filter"] = error_filter

            # process raw filter list
            if self.m_ui.rawFilterEdit.text():
                pass  # TODO current ui not sufficient to reflect this param

            # process bitrate
            bitrate = self.m_ui.bitrateBox.bit_rate()
            if bitrate > 0:
                self.m_currentSettings.configurations[" bitrate"] = bitrate

            # process CAN FD setting
            self.m_currentSettings.configurations["fd"] = self.m_ui.canFdBox.currentData()

            # process data bitrate
            data_bitrate = self.m_ui.dataBitrateBox.bit_rate()
            if data_bitrate > 0:
                self.m_currentSettings.configurations["data_bitrate"] = data_bitrate
