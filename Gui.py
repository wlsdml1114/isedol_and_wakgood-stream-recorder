import sys
import os
import yaml

from multiprocessing import Process
from recorder_process import RecorderProcess
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QGroupBox, QLineEdit, QCheckBox, QPushButton, QGridLayout, QVBoxLayout, QLabel, QFileDialog, QMessageBox

class MyApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.GetConfigure()
        self.initUI()

    def initUI(self):
        wid = QWidget()
        startbutton = QPushButton('Stream Record Start')
        def StartTwitchRecorder():
            
            checked_list = [self.config["USER_ID"][idx] for idx, ch in enumerate(self.checkbox_list) if ch.isChecked()]
            print(checked_list)
            if len(checked_list) == 0:
                QMessageBox.information(self,"Warning","Nobody selected")
            elif self.app_id_text.text() == "":
                QMessageBox.information(self,"Warning","Client id must need for recording")
            elif self.app_pw_text.text() == "":
                QMessageBox.information(self,"Warning","Client secret must need for recording")
            elif not(os.path.exists(self.path_label_text.text())):
                QMessageBox.information(self,"Warning","Wrong path")
            else :
                QMessageBox.information(self,"Information","Recording will start\n%s"%(", ".join(checked_list)))
                self.proc = [
                    Process(target=RecorderProcess, args=(
                            self.path_label_text.text(),
                            user,
                            self.app_id_text.text(),
                            self.app_pw_text.text()
                    )) for user in checked_list
                ]
                [multi.start() for multi in self.proc]


        startbutton.clicked.connect(StartTwitchRecorder)

        vbox = QVBoxLayout()
        vbox.addWidget(self.UserInformationGroup())
        vbox.addWidget(self.StreamerSelection())
        vbox.addWidget(startbutton)

        wid.setLayout(vbox)
        self.setCentralWidget(wid)

        self.setWindowTitle('Twitch Recoder Ver.0.1.0')
        self.setGeometry(300, 300, 480, 320)
        self.show()
    
    def GetConfigure(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'config.yaml'),encoding='utf-8') as file:
            self.config = yaml.load(file,Loader=yaml.FullLoader)
        
    
    def UserInformationGroup(self):
        groupbox = QGroupBox('User Information')

        app_id_label = QLabel('Client ID')
        app_id_label.setAlignment(Qt.AlignVCenter)
        app_pw_label = QLabel('Client secret')
        app_pw_label.setAlignment(Qt.AlignVCenter)
        path_label = QLabel('Change Path')
        path_label.setAlignment(Qt.AlignVCenter)
        now_path_label = QLabel('Now Path')
        now_path_label.setAlignment(Qt.AlignVCenter)
        self.app_id_text = QLineEdit(self.config["CLIENT_ID"])
        self.app_pw_text = QLineEdit(self.config["CLIENT_SECRET"])
        self.path_label_text = QLabel(self.config["ROOT_PATH"])
        pushbutton = QPushButton('Change Path')

        def GetVideoPath():
            fname = QFileDialog.getExistingDirectory(self,'Open folder', './')
            if fname != "":
                self.path_label_text.setText(fname)

        pushbutton.clicked.connect(GetVideoPath)

        grid = QGridLayout()
        grid.addWidget(app_id_label,0,0)
        grid.addWidget(app_pw_label,1,0)
        grid.addWidget(path_label,2,0)
        grid.addWidget(now_path_label,3,0)
        grid.addWidget(self.app_id_text,0,1)
        grid.addWidget(self.app_pw_text,1,1)
        grid.addWidget(pushbutton,2,1)
        grid.addWidget(self.path_label_text,3,1)

        groupbox.setLayout(grid)

        return groupbox
    
    def StreamerSelection(self):

        groupbox = QGroupBox('Select Streamer')

        all = QPushButton('전체 선택')
        all_bool = True
        
        self.checkbox_list = [QCheckBox(text) for text in self.config["CHECKBOX_NAME"]]
        self.checkbox_list[0].setChecked(True)

        # wak = QCheckBox('왁굳형')
        # ine = QCheckBox('아이네')
        # jing = QCheckBox('징버거')
        # lilpa = QCheckBox('릴파')
        # jururu = QCheckBox('주르르')
        # gosegu = QCheckBox('고세구')
        # viichan = QCheckBox('비챤')

        def OnClickEvent():
            nonlocal all_bool
            if all_bool :
                all_bool = False
                all.setText("전체 취소")
                for ckb in self.checkbox_list : ckb.setChecked(True)
                # wak.setChecked(True)
                # ine.setChecked(True)
                # jing.setChecked(True)
                # lilpa.setChecked(True)
                # jururu.setChecked(True)
                # gosegu.setChecked(True)
                # viichan.setChecked(True)
            else:
                all_bool = True
                all.setText("전체 선택")
                for ckb in self.checkbox_list : ckb.setChecked(False)
                # wak.setChecked(False)
                # ine.setChecked(False)
                # jing.setChecked(False)
                # lilpa.setChecked(False)
                # jururu.setChecked(False)
                # gosegu.setChecked(False)
                # viichan.setChecked(False)

        all.clicked.connect(OnClickEvent)

        grid = QGridLayout()
        grid.addWidget(self.checkbox_list[0],0,0)        # wak
        grid.addWidget(all,1,0)
        grid.addWidget(self.checkbox_list[1],0,1)        # ine
        grid.addWidget(self.checkbox_list[2],0,2)        # jing
        grid.addWidget(self.checkbox_list[3],0,3)        # lilpa
        grid.addWidget(self.checkbox_list[4],1,1)        # jururu
        grid.addWidget(self.checkbox_list[5],1,2)        # gosegu
        grid.addWidget(self.checkbox_list[6],1,3)        # viichan


        groupbox.setLayout(grid)

        return groupbox
    
    def closeEvent(self, a0: QCloseEvent) -> None:
        print("kill")
        [multi.kill() for multi in self.proc]
        return super().closeEvent(a0)
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())