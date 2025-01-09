# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from PySide6.QtWidgets import QDialog

from ui_about import Ui_AboutDialog


class AboutDialog(QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.m_ui = Ui_AboutDialog()
        self.m_ui.setupUi(self)
        self.m_ui.pushButton.pressed.connect(self.close)
