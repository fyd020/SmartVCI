from PySide6.QtCore import QSize, Qt, Signal, QObject, QMimeData
from PySide6.QtGui import QIcon, QAction, QMouseEvent, QDragEnterEvent, QDropEvent, QDrag
from PySide6.QtWidgets import (QApplication, QDialog, QPushButton, QHBoxLayout, QMessageBox,
                               QMainWindow, QGridLayout, QLabel, QLineEdit, QWidget)
import sys


class Communicate(QObject):
    close_app = Signal()


class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        self.c = None
        self.label = None
        self.text = None
        self.init_ui()

    def init_ui(self):
        exit_act = QAction(QIcon(r"icon\JiDu.ico"), "&Exit", self)
        grid = QGridLayout()
        x = 0
        y = 0
        self.text = f"x:{x},y:{y}"
        self.label = QLabel(self.text, self)
        grid.addWidget(self.label, 0, 0, Qt.AlignmentFlag.AlignTop)
        self.setMouseTracking(True)
        self.setLayout(grid)
        btn1 = QPushButton("Button 1", self)
        btn1.move(30, 50)
        btn2 = QPushButton("Button 2", self)
        btn2.move(150, 50)
        btn1.clicked.connect(self.button_clicked)
        btn2.clicked.connect(self.button_clicked)
        self.c = Communicate()
        self.c.close_app.connect(self.close)
        edit = QLineEdit("", self)
        edit.setDragEnabled(True)
        edit.move(280, 50)
        exit_act.setShortcut("Ctrl+Q")
        exit_act.setStatusTip("Exit application")
        exit_act.triggered.connect(QApplication.instance().quit)
        self.statusBar().showMessage("v0.1")
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(exit_act)
        self.setGeometry(518, 518, 618, 318)
        self.setWindowTitle("JiDU SDK")
        self.show()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        x = int(event.position().x())
        y = int(event.position().y())
        text = f"x: {x}, y: {y}"
        self.label.setText(text)

    def button_clicked(self):
        sender = self.sender()
        msg = f"{sender.text()} was pressed"
        self.statusBar().showMessage(msg)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.c.close_app.emit()


class Button(QPushButton):
    def __init__(self, title, parent):
        super().__init__(title, parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasFormat("text/plain"):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        self.setText(event.mimeData().text())

    def mouseMoveEvent(self, e: QMouseEvent) -> None:
        if e.buttons() != Qt.MouseButton.RightButton:
            return
        mime_data = QMimeData()
        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.setHotSpot(e.position().toPoint() - self.rect().topLeft())
        drop_action = drag.exec(Qt.DropAction.MoveAction)

    def mousePressEvent(self, e: QMouseEvent) -> None:
        super().mouseMoveEvent(e)
        if e.button() == Qt.MouseButton.LeftButton:
            print("press")


class Example1(QWidget):
    def __init__(self):
        super().__init__()
        self.button = None
        self.init_ui()

    def init_ui(self):
        self.setAcceptDrops(True)
        self.button = Button("Button", self)
        self.button.move(100, 65)
        self.setWindowTitle("Click or Move")
        self.setGeometry(300, 300, 550, 450)

    def dragEnterEvent(self, e: QDragEnterEvent) -> None:
        e.accept()

    def dropEvent(self, e: QDropEvent) -> None:
        position = e.position()
        self.button.move(position.toPoint())
        e.setDropAction(Qt.DropAction.MoveAction)
        e.accept()


def main():
    app = QApplication(sys.argv)
    ex = Example1()
    ex.show()
    sys.exit(app.exec())


class demo1:

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = QDialog()
        self.window.setWindowTitle("JiDU SDK")
        icon = QIcon()
        icon.addFile(r"D:\JiDU\图标\jidu.jpg")
        # icon.actualSize(QSize(60, 41), QIcon.Mode.Normal)
        self.window.setWindowIcon(icon)
        self.window.resize(400, 300)

    def show_msg(self):
        QMessageBox.information(self.window, "信息提示", "你点击了我")

    def show(self):
        hbox = QHBoxLayout()
        button = QPushButton("点击我")
        button.clicked.connect(self.show_msg)
        hbox.addWidget(button)
        self.window.setLayout(hbox)
        self.window.show()
        sys.exit(self.app.exec())


if __name__ == '__main__':
    main()
    # demo1().show()
