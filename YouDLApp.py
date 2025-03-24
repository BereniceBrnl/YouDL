from kivy.config import Config

Config.set('graphics', 'width', '412')
Config.set('graphics', 'height', '915')

import os

#necessary to avoid crashes due to a denial access to YouTube. Python conflict with android it seems.
#source : https://stackoverflow.com/questions/72306952/error-in-pytube-urlopen-error-ssl-certificate-verify-failed-certificate-veri
import ssl
ssl._create_default_https_context = ssl._create_stdlib_context

from kivymd.app import MDApp
from kivy.core.text import LabelBase
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.screen import MDScreen
from kivy.utils import platform
from pytubefix import YouTube #use of pytubefix until pytube is fix
#from pytube import YouTube
from kivy.lang import Builder
from re import sub


#need the use of the builder since the .py file will not have the same name as the .kv file
#buildozer needs a main.py
#Builder.load_file('YouDL.kv')

class HomeScreen(MDScreen):

    def on_enter(self):

        #erase former input in case we go back to the Home Screen
        self.ids.input.text = ""

    def get_url(self):

        #check if url if indeed Youtube, else keep trying
        YouDLApp.url = self.ids.input.text
        try:
            YouDLApp.yt = YouTube(YouDLApp.url)
            YouDLApp.sm.current = "validation_screen"
        except:
            self.ids.input.error = True
            self.ids.input.hint_text = "This was not a valid YouTube URL."
            self.ids.input.text = ""

class ValidationScreen(MDScreen):

    def on_enter(self):

        #show title of the video + thumbnail
        self.ids.video_title.text = YouDLApp.yt.title
        self.ids.thumbnail.source = YouDLApp.yt.thumbnail_url

    def download_audio(self):

        #set path to default download folder
        path_download = '/Users/berenicebrunel/Downloads'
        

        #download the first audio stream available
        try:
            audio = YouDLApp.yt.streams.filter(only_audio=True, file_extension='mp4').first()
            title = audio.title
            file_name = sub("\W", "_", title) #clean the file name of any special character or the app won't find the file to convert it to .mp3
            audio.download(output_path=path_download, filename=file_name)
        except:
            YouDLApp.sm.current = "error_screen"

        #convert the .mp4 file to .mp3
        base, ext = os.path.splitext(path_download + "/" + file_name + ".mp4")
        YouDLApp.mp3_file = base + ".mp3"
        os.rename(path_download + "/" + file_name, YouDLApp.mp3_file)

        YouDLApp.sm.current = "download_screen"


class DownloadScreen(MDScreen):
    def on_enter(self):
        self.ids.file_name.text = YouDLApp.mp3_file
        self.ids.thumbnail.source = YouDLApp.yt.thumbnail_url

class ErrorScreen(MDScreen):
    pass

class YouDLApp(MDApp):

    #need to access these variables in other classes
    url = ""
    sm = ScreenManager()
    video_title = ""
    thumbnail = ""
    yt = ""
    mp3_file =""


    def build(self):

        #need to request for permissions to avoid crashes even if permissions declared in buildozer.spec
        if platform == "android":
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.INTERNET, Permission.READ_EXTERNAL_STORAGE])

        LabelBase.register(name="londrina", fn_regular="data/LondrinaShadow-Regular.ttf") #source: https://fonts.google.com/specimen/Jersey+10
        LabelBase.register(name="gaegu", fn_regular="data/Gaegu-Regular.ttf")
        LabelBase.register(name="roboto", fn_regular="data/Roboto-Thin.ttf")

        #self.theme_cls.theme_style = "Dark"
        self.sm.add_widget(HomeScreen(name="home_screen"))
        self.sm.add_widget(ValidationScreen(name="validation_screen"))
        self.sm.add_widget(DownloadScreen(name="download_screen"))
        self.sm.add_widget(ErrorScreen(name="error_screen"))
        self.sm.current = "home_screen"
        return self.sm

YouDLApp().run()