import os
import yaml
import argparse

from recorder_docker import TwitchRecorder

class Recorder():

    USER_ID =[
        "woowakgood",
        "vo_ine",
        "jingburger",
        "lilpaaaaaa",
        "cotton__123",
        "gosegugosegu",
        "viichan6"
    ]
    CHECKBOX_NAME=[
        "우왁굳",
        "아이네",
        "징버거",
        "릴파",
        "주르르",
        "고세구",
        "비챤"
    ]

    def __init__(self):
        self.GetConfigure()
        self.GetArg()

    def GetArg(self):
        arg = argparse.ArgumentParser(description="write streamer name or ID")
        arg.add_argument('--name', default=None, required= False)

        self.name = arg.parse_args().name
        if self.name == None:
            self.name = input('streamer ID or name : ')
        self.NameCheck()

    def NameCheck(self):
        if self.name in self.CHECKBOX_NAME:
            print("user name is in name list")
            self.user_id = self.USER_ID[self.CHECKBOX_NAME == self.name]
        elif self.name in self.USER_ID :
            print("user id is in name list")
            self.user_id = self.name
        else:
            print("user id isn't in name list")
            self.user_id = self.name

    def ConfigureCheck(self):
        if self.config == None :
            self.AppIdCheck()
            self.AppSecretCheck()
        else :
            if self.config['CLIENT_ID'] == "":
                self.AppIdCheck()
            else :
                self.app_id = self.config['CLIENT_ID']
            if self.config['CLIENT_SECRET'] == "":
                self.AppSecretCheck()
            else :
                self.app_secret = self.config['CLIENT_SECRET']
        self.PathCheck()

    def AppIdCheck(self):
        self.app_id = input('app id :')
        print('your app id is ', self.app_id)
    
    def AppSecretCheck(self):
        self.app_secret = input('app secret :')
        print('your app secret is ', self.app_secret)
    
    def PathCheck(self):
        self.path = input('stream video save path (default = running file directory) : ')
        if os.path.exists(self.path):
            print('your video save path is ', self.path)
        else :
            self.path = os.path.dirname(os.path.abspath(__file__))
            print('wrong path\nyour video save path is ', self.path)

    def run(self):
        recorder = TwitchRecorder(self.path, self.user_id, self.app_id, self.app_secret)
        recorder.run()

    def GetConfigure(self):
        try:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'config.yaml'),encoding='utf-8') as file:
                self.config = yaml.load(file,Loader=yaml.FullLoader)
        except:
            print("config.yaml file doesn't exist")
            self.config = None
        
        self.ConfigureCheck()
        
    
if __name__ == '__main__':
    recorder = Recorder()
    recorder.run()
