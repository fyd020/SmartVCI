# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'busdeviceinfodialog.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
                           QFont, QFontDatabase, QGradient, QIcon,
                           QImage, QKeySequence, QLinearGradient, QPainter,
                           QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QPushButton,
                               QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

from busdeviceinfobox import BusDeviceInfoBox


class Ui_BusDeviceInfoDialog(object):
    def setupUi(self, BusDeviceInfoDialog):
        if not BusDeviceInfoDialog.objectName():
            BusDeviceInfoDialog.setObjectName(u"BusDeviceInfoDialog")
        BusDeviceInfoDialog.resize(237, 225)
        self.verticalLayout = QVBoxLayout(BusDeviceInfoDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.deviceInfoBox = BusDeviceInfoBox(BusDeviceInfoDialog)
        self.deviceInfoBox.setObjectName(u"deviceInfoBox")
        self.deviceInfoBox.setEnabled(True)

        self.verticalLayout.addWidget(self.deviceInfoBox)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.okButton = QPushButton(BusDeviceInfoDialog)
        self.okButton.setObjectName(u"okButton")

        self.horizontalLayout.addWidget(self.okButton)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(BusDeviceInfoDialog)

        self.okButton.setDefault(True)

        QMetaObject.connectSlotsByName(BusDeviceInfoDialog)

    # setupUi

    def retranslateUi(self, CanBusDeviceInfoDialog):
        CanBusDeviceInfoDialog.setWindowTitle(
            QCoreApplication.translate("BusDeviceInfoDialog", u"Device Properties", None))
        self.deviceInfoBox.setTitle(QCoreApplication.translate("BusDeviceInfoDialog", u"Device Properties", None))
        self.okButton.setText(QCoreApplication.translate("BusDeviceInfoDialog", u"Ok", None))
    # retranslateUi
