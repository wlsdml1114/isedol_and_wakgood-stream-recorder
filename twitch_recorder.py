import datetime
import os
import subprocess
import shutil
import time
import requests

from twitch_response_status import TwitchResponseStatus
from twitch_recorder_log_handler import TwitchRecorderLogHandler
from PyQt5.QtCore import pyqtSignal, QThread, pyqtSlot


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