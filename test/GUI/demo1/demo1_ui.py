# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'demo1.ui'
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
from PySide6.QtWidgets import (QApplication, QLabel, QSizePolicy, QWidget)


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"JiDU")
        Form.resize(218, 218)
        icon = QIcon()
        # iconThemeName = u"accessories-dictionary"
        # if QIcon.hasThemeIcon(iconThemeName):
        #     icon = QIcon.fromTheme(iconThemeName)
        # else:
        icon.addFile(u"../jidu.jpg", QSize(), QIcon.Normal, QIcon.Off)

        Form.setWindowIcon(icon)
        self.label = QLabel(Form)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(80, 100, 91, 16))

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"JiDU", None))
        self.label.setText(QCoreApplication.translate("Form", u"Hello! World!", None))
    # retranslateUi
