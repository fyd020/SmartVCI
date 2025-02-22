# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtWidgets import QDialog

from ui_busdeviceinfodialog import Ui_BusDeviceInfoDialog


class BusDeviceInfoDialog(QDialog):

    def __init__(self, info, parent):
        super().__init__(parent)
        self.m_ui = Ui_BusDeviceInfoDialog()
        self.m_ui.setupUi(self)
        self.m_ui.deviceInfoBox.set_device_info(info)
        self.m_ui.okButton.pressed.connect(self.close)
