# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'busdeviceinfobox.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QGroupBox, QLabel,
                               QSizePolicy, QVBoxLayout, QWidget)


class Ui_BusDeviceInfoBox(object):
    def setupUi(self, BusDeviceInfoBox):
        if not BusDeviceInfoBox.objectName():
            BusDeviceInfoBox.setObjectName(u"BusDeviceInfoBox")
        BusDeviceInfoBox.resize(319, 217)
        self.verticalLayout = QVBoxLayout(BusDeviceInfoBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.pluginLabel = QLabel(BusDeviceInfoBox)
        self.pluginLabel.setObjectName(u"pluginLabel")

        self.verticalLayout.addWidget(self.pluginLabel)

        self.nameLabel = QLabel(BusDeviceInfoBox)
        self.nameLabel.setObjectName(u"nameLabel")

        self.verticalLayout.addWidget(self.nameLabel)

        self.descriptionLabel = QLabel(BusDeviceInfoBox)
        self.descriptionLabel.setObjectName(u"descriptionLabel")

        self.verticalLayout.addWidget(self.descriptionLabel)

        self.serialNumberLabel = QLabel(BusDeviceInfoBox)
        self.serialNumberLabel.setObjectName(u"serialNumberLabel")

        self.verticalLayout.addWidget(self.serialNumberLabel)

        self.aliasLabel = QLabel(BusDeviceInfoBox)
        self.aliasLabel.setObjectName(u"aliasLabel")

        self.verticalLayout.addWidget(self.aliasLabel)

        self.channelLabel = QLabel(BusDeviceInfoBox)
        self.channelLabel.setObjectName(u"channelLabel")

        self.verticalLayout.addWidget(self.channelLabel)

        self.isFlexibleDataRateCapable = QCheckBox(BusDeviceInfoBox)
        self.isFlexibleDataRateCapable.setObjectName(u"isFlexibleDataRateCapable")
        self.isFlexibleDataRateCapable.setEnabled(True)
        self.isFlexibleDataRateCapable.setCheckable(True)

        self.verticalLayout.addWidget(self.isFlexibleDataRateCapable)

        self.retranslateUi(BusDeviceInfoBox)

        QMetaObject.connectSlotsByName(BusDeviceInfoBox)

    # setupUi

    def retranslateUi(self, CanBusDeviceInfoBox):
        CanBusDeviceInfoBox.setWindowTitle(QCoreApplication.translate("BusDeviceInfoBox", u"Device Properties", None))
        self.pluginLabel.setText("")
        self.nameLabel.setText("")
        self.descriptionLabel.setText("")
        self.serialNumberLabel.setText("")
        self.aliasLabel.setText("")
        self.channelLabel.setText("")
        self.isFlexibleDataRateCapable.setText(
            QCoreApplication.translate("BusDeviceInfoBox", u"Flexible Data Rate", None))
    # retranslateUi
