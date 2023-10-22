import configparser
import ctypes
from time import sleep
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
from bs4 import BeautifulSoup

from url_generator import fetch_urls

class StreamController:
    def __init__(self):
        self.init_browser()
        self.init_config()

        self.volume = 0.0
        self.video_playing = False
        self.muted = False

    def init_browser(self):
        chromedriver_autoinstaller.install()
        chrome_options = self.load_adblocker_extension()
        self.browser = webdriver.Chrome(options=chrome_options)

    def init_config(self, config_filepath="../config.ini"):
        config = configparser.ConfigParser()
        config.read(config_filepath)

        self.default_config = config["DEFAULT"]
        self.preset = self.default_config["PRESET"]
        self.preset_config = config[self.preset]

    def construct_base_url(self):
        stream_base_url = self.preset_config["STREAM_BASE_URL"]
        video_name = self.preset_config["VIDEO_NAME"]
        video_type = self.preset_config["VIDEO_TYPE"]
        video_number = self.preset_config["VIDEO_NUMBER"]
        video_url_format = self.preset_config["VIDEO_URL_FORMAT"]

        video_url = video_url_format.format(stream_base_url=stream_base_url, video_name=video_name, video_type=video_type, video_number=video_number)

        return video_url

    def run(self):
        video_url = self.construct_url()
        black_url_keywords = self.preset_config["BLACKLIST_URL_KEYWORDS"].split(",")

        url_list = fetch_urls(self.preset, base_url, black_url_keywords)

        for url in url_list:
            self.browser.get(url)
            
            self.hwnd = self.get_window_handle()

            print("\a")
            # sleep(10)

            self.video_element = self.browser.find_element(By.TAG_NAME, "video")
            self.browser.find_element(By.TAG_NAME, "body").click()
            self.toggle_play()

            # self.toggle_mute()

            self.change_volume(+1)

            print("DONE")

            sleep(1000)
            
            self.browser.exit()

    def change_volume(self, direction):
        volume_amount = self.volume + float(self.default_config["VOLUME_AMOUNT"]) * direction

        if (volume_amount > 1.0):
            volume_amount = 1.0
        elif (volume_amount < 0.0):
            volume_amount = 0.0

        script = "arguments[0].volume={volume_amount}".format(volume_amount=volume_amount)
        self.browser.execute_script(script, self.video_element)
        self.volume = volume_amount

    def toggle_mute(self):
        if (self.muted):
            self.browser.execute_script("arguments[0].muted=false;", self.video_element)
            self.muted = False
        else:
            self.browser.execute_script("arguments[0].muted=true;", self.video_element)
            self.muted = True

    def toggle_play(self):
        if (self.video_playing):
            self.browser.execute_script("arguments[0].pause();", self.video_element)
            self.video_playing = False
        else:
            self.browser.execute_script("arguments[0].play();", self.video_element)
            self.video_playing = True

    def seek(self, direction):
        script = "arguments[0].currentTime += {seek_amount};".format(seek_amount=float(self.default_config["SEEK_AMOUNT"]) * direction)
        self.browser.execute_script(script, self.video_element)

    # def next_video(self):
    # def previous_video(self):

    # def skip_intro(self):

    def load_adblocker_extension(self, adblocker_extension_filepath="../resources/extensions/ublock_origin_21_10_23.crx"):
        chrome_options = webdriver.chrome.options.Options()
        chrome_options.add_extension(adblocker_extension_filepath)

        return chrome_options

    def get_window_handle(self):
        hwnd = ctypes.windll.user32.GetForegroundWindow()

        return hwnd

    def check_window_focus(self):
        return self.get_window_handle() == self.hwnd

    def set_window_focus(self):
        user32 = ctypes.windll.user32
        user32.SetForegroundWindow(self.hwnd)
        if user32.IsIconic(self.hwnd):
            user32.ShowWindow(self.hwnd, 9)


if __name__ == "__main__":
    controller = Controller()
    controller.run()
