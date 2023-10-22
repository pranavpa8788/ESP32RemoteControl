import configparser
import ctypes
from time import sleep
import asyncio

from playwright.async_api import async_playwright

from url_generator import fetch_urls

class StreamController:
    def __init__(self):
        self.volume = 0.0
        self.video_playing = False
        self.muted = False

    async def initialize(self):
        async with async_playwright() as playwright:
            await self.init_browser(playwright)
            self.init_config()

            await self.run()

    async def init_browser(self, playwright):
        # Extension installed manually since using sessions
        #adblocker_extension_filepath = "../resources/extensions/ublock_origin_21_10_23.crx"

        user_data_dir = "../profiles/nathan"
        self.browser = await playwright.firefox.launch_persistent_context(user_data_dir, headless=False)
        self.page = await self.browser.new_page()

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

    async def run(self):
        video_url = self.construct_base_url()
        black_url_keywords = self.preset_config["BLACKLIST_URL_KEYWORDS"].split(",")

        url_list = fetch_urls(self.preset, video_url, black_url_keywords)

        for url in url_list:
            await self.page.goto(url)
            
            self.hwnd = self.get_window_handle()

            self.video_element = self.page.locator("video")
            print(self.video_element)
            # self.video_element = self.browser.find_element(By.TAG_NAME, "video")
            await self.page.locator("body").click()
            # self.browser.find_element(By.TAG_NAME, "body").click()
            await self.toggle_play()
            await self.change_volume(1, volume_amount=1.0)

            await self.toggle_play()

            sleep(10)

            await self.toggle_play()

            sleep(1000)

    async def change_volume(self, direction=1, volume_amount=None):
        if volume_amount is None:
            volume_amount = self.volume + float(self.default_config["VOLUME_AMOUNT"]) * direction

        if (volume_amount > 1.0):
            volume_amount = 1.0
        elif (volume_amount < 0.0):
            volume_amount = 0.0

        script = "video_element => video_element.volume={volume_amount}".format(volume_amount=volume_amount)
        await self.video_element.evaluate(script)

        self.volume = volume_amount

    async def toggle_mute(self):
        if (self.muted):
            await self.video_element.evaluate("video_element => video_element.muted=false;")
            self.muted = False
        else:
            await self.video_element.evaluate("video_element => video_element.muted=true;")
            self.muted = True

    async def toggle_play(self):
        if self.video_playing:
            await self.video_element.evaluate('video_element => video_element.pause();')
            self.video_playing = False
        else:
            await self.video_element.evaluate('video_element => video_element.play();')
            self.video_playing = True

    async def seek(self, direction):
        script = "video_element => video_element.currentTime += {seek_amount};".format(seek_amount=float(self.default_config["SEEK_AMOUNT"]) * direction)
        await self.video_element.evaluate(script)

    # def next_video(self):
    # def previous_video(self):

    # def skip_intro(self):

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
    stream_controller = StreamController()
    asyncio.run(stream_controller.initialize())
