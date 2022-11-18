from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QTextEdit
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QCloseEvent
from twitch_recorder import TwitchRecorder

class RecorderWindow(QMainWindow):

    close_signal = pyqtSignal(bool)

    def __init__(self, root_path, username, client_id, client_secret):
        super().__init__()
        self.initUI()
        self.recorder = TwitchRecorder(root_path, username, client_id, client_secret)
        self.recorder.recorder_log.connect(self.LogUpdate)
        self.close_signal.connect(self.recorder.GetCloseSignal)
        self.recorder.start()
        self.setStyleSheet("color: black;" "background-color: white;")
        self.setGeometry(500,500,700,450)

        self.show()
        

    def initUI(self):
        camwid = QWidget()
       
        main_layout = QGridLayout()
        self.fps_label = QTextEdit()
        self.fps_label.setEnabled(False)

        main_layout.addWidget(self.fps_label)
        camwid.setLayout(main_layout)
        self.setCentralWidget(camwid)

    @pyqtSlot(str)
    def LogUpdate(self, log):
        self.fps_label.append(log)

    def ExitRecorder(self):
        self.close_signal.emit(True)

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.ExitRecorder()
        return super().closeEvent(a0)