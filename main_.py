import sys
import os
import yaml
import datetime
import os
import subprocess
import shutil
import time
import requests
import enum 

from multiprocessing import Process
from recorder_process import RecorderProcess
from PyQt5.QtCore import pyqtSignal, QThread, pyqtSlot, Qt
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QApplication, QWidget, QGroupBox, QLineEdit, QCheckBox, QPushButton, QGridLayout, QVBoxLayout, QLabel, QFileDialog, QMessageBox


class TwitchResponseStatus(enum.Enum):
    ONLINE = 0
    OFFLINE = 1
    NOT_FOUND = 2
    UNAUTHORIZED = 3
    ERROR = 4

class TwitchRecorder(QThread):

    recorder_log = pyqtSignal(str)

    def __init__(self, root_path, username, client_id, client_secret):
        super().__init__()
        # logging.basicConfig(filename="twitch-recorder.log", level=logging.INFO)
        # logging.getLogger().addHandler(logging.StreamHandler())
        # logging.getLogger().addHandler(TwitchRecorderLogHandler(target_widget))
        # global configuration
        self.ffmpeg_path = "ffmpeg"
        self.disable_ffmpeg = False
        self.refresh = 15
        self.root_path = root_path

        # user configuration
        self.username = username
        self.quality = "best"

        # twitch configuration
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = "https://id.twitch.tv/oauth2/token?client_id=" + self.client_id + "&client_secret=" \
                         + self.client_secret + "&grant_type=client_credentials"
        self.url = "https://api.twitch.tv/helix/streams"
        self.access_token = self.fetch_access_token()

        self.looping = True

    @pyqtSlot(bool)
    def GetCloseSignal(self, signal):
        if signal :
            if self.p != None:
                self.p.kill()
                self.looping=False
                self.quit()
                self.wait(3000)
    
    def SendLog(self, str):
        self.recorder_log.emit(str)

    def stop(self):
        self.looping=False
        self.quit()
        self.wait(3000)

    def fetch_access_token(self):
        token_response = requests.post(self.token_url, timeout=15)
        token_response.raise_for_status()
        token = token_response.json()
        return token["access_token"]

    def run(self):
        # path to recorded stream
        recorded_path = os.path.join(self.root_path, "recorded", self.username)
        # path to finished video, errors removed
        processed_path = os.path.join(self.root_path, "processed", self.username)

        # create directory for recordedPath and processedPath if not exist
        if os.path.isdir(recorded_path) is False:
            os.makedirs(recorded_path)
        if os.path.isdir(processed_path) is False:
            os.makedirs(processed_path)

        # make sure the interval to check user availability is not less than 15 seconds
        if self.refresh < 15:
            self.SendLog("check interval should not be lower than 15 seconds")
            # logging.warning("check interval should not be lower than 15 seconds")
            self.refresh = 15
            self.SendLog("system set check interval to 15 seconds")
            # logging.info("system set check interval to 15 seconds")

        # fix videos from previous recording session
        try:
            video_list = [f for f in os.listdir(recorded_path) if os.path.isfile(os.path.join(recorded_path, f))]
            if len(video_list) > 0:
                self.SendLog("processing previously recorded files")
                # logging.info("processing previously recorded files")
            for f in video_list:
                recorded_filename = os.path.join(recorded_path, f)
                processed_filename = os.path.join(processed_path, f)
                self.process_recorded_file(recorded_filename, processed_filename)
        except Exception as e:
            self.SendLog(e)
            # logging.error(e)
        self.SendLog("checking for %s every %s seconds, recording with %s quality"%(
                        self.username, 
                        self.refresh, 
                        self.quality
                     )
                    )
        # logging.info("checking for %s every %s seconds, recording with %s quality",
        #              self.username, self.refresh, self.quality)
        self.loop_check(recorded_path, processed_path)

    def process_recorded_file(self, recorded_filename, processed_filename):
        if self.disable_ffmpeg:
            self.SendLog("moving: %s"%(recorded_filename))
            # logging.info("moving: %s", recorded_filename)
            shutil.move(recorded_filename, processed_filename)
        else:
            self.SendLog("fixing: %s"%(recorded_filename))
            # logging.info("fixing %s", recorded_filename)
            self.ffmpeg_copy_and_fix_errors(recorded_filename, processed_filename)

    def ffmpeg_copy_and_fix_errors(self, recorded_filename, processed_filename):
        try:
            subprocess.call(
                [self.ffmpeg_path, "-err_detect", "ignore_err", "-i", recorded_filename, "-c", "copy",
                 processed_filename])
            os.remove(recorded_filename)
        except Exception as e:
            self.SendLog(e)
            # logging.error(e)

    def check_user(self):
        info = None
        status = TwitchResponseStatus.ERROR
        try:
            headers = {"Client-ID": self.client_id, "Authorization": "Bearer " + self.access_token}
            r = requests.get(self.url + "?user_login=" + self.username, headers=headers, timeout=15)
            r.raise_for_status()
            info = r.json()
            if info is None or not info["data"]:
                status = TwitchResponseStatus.OFFLINE
            else:
                status = TwitchResponseStatus.ONLINE
        except requests.exceptions.RequestException as e:
            if e.response:
                if e.response.status_code == 401:
                    status = TwitchResponseStatus.UNAUTHORIZED
                if e.response.status_code == 404:
                    status = TwitchResponseStatus.NOT_FOUND
        return status, info

    def loop_check(self, recorded_path, processed_path):
        while self.looping:
            status, info = self.check_user()
            if status == TwitchResponseStatus.NOT_FOUND:
                self.SendLog("username not found, invalid username or typo")
                # logging.error("username not found, invalid username or typo")
                time.sleep(self.refresh)
            elif status == TwitchResponseStatus.ERROR:
                self.SendLog("%s unexpected error. will try again in 5 minutes"%(
                              datetime.datetime.now().strftime("%Hh%Mm%Ss")))
                # logging.error("%s unexpected error. will try again in 5 minutes",
                #               datetime.datetime.now().strftime("%Hh%Mm%Ss"))
                time.sleep(300)
            elif status == TwitchResponseStatus.OFFLINE:
                self.SendLog("%s currently offline, checking again in %s seconds"%(self.username, self.refresh))
                # logging.info("%s currently offline, checking again in %s seconds", self.username, self.refresh)
                time.sleep(self.refresh)
            elif status == TwitchResponseStatus.UNAUTHORIZED:
                self.SendLog("unauthorized, will attempt to log back in immediately")
                # logging.info("unauthorized, will attempt to log back in immediately")
                self.access_token = self.fetch_access_token()
            elif status == TwitchResponseStatus.ONLINE:
                self.SendLog("%s online, stream recording in session"%(self.username))
                # logging.info("%s online, stream recording in session", self.username)

                channels = info["data"]
                channel = next(iter(channels), None)
                filename = self.username + " - " + datetime.datetime.now() \
                    .strftime("%Y-%m-%d %Hh%Mm%Ss") + " - " + channel.get("title") + ".mp4"

                # clean filename from unnecessary characters
                filename = "".join(x for x in filename if x.isalnum() or x in [" ", "-", "_", "."])

                recorded_filename = os.path.join(recorded_path, filename)
                processed_filename = os.path.join(processed_path, filename)

                command = ["streamlink", "--twitch-disable-ads", "twitch.tv/" + self.username, self.quality, "-o", recorded_filename]

                # start streamlink process
                # subprocess.call(command)

                # self.p = subprocess.Popen(
                #     command,
                #     stdout= subprocess.PIPE,
                #     stderr= subprocess.STDOUT,
                #     universal_newlines=True,
                #     shell=True
                # )

                self.p = subprocess.run(["start", "/wait", "cmd", "/K", *command], shell=True)

                # while self.p.poll() ==None :
                #     out = p.stdout.readline()
                #     out = self.p.communicate()
                #     self.SendLog(out)

                self.SendLog("recording stream is done, processing video file")
                # logging.info("recording stream is done, processing video file")
                if os.path.exists(recorded_filename) is True:
                    self.process_recorded_file(recorded_filename, processed_filename)
                else:
                    self.SendLog("skip fixing, file not found")
                    # logging.info("skip fixing, file not found")
                self.SendLog("processing is done, going back to checking...")
                # logging.info("processing is done, going back to checking...")
                time.sleep(self.refresh)

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