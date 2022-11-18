from multiprocessing import Process
from PyQt5.QtWidgets import QApplication
from recorder_window import RecorderWindow

class RecorderProcess(Process):
    def __init__(self, root_path, username, client_id, client_secret):
        app = QApplication.instance()
        if app is not None:
            print("QApp already exists in child process.")
        else:
            app = QApplication([])
        
        self.cam_win = RecorderWindow(root_path, username, client_id, client_secret)

        self.cam_win.setWindowTitle("%s twitch recorder log"%(username))
        self.cam_win.show()
        app.exec_()
        