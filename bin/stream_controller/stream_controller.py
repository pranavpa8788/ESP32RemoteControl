import configparser
import ctypes
from time import sleep
import asyncio
import os

from playwright.async_api import async_playwright

# from url_generator import fetch_urls
from stream_controller import url_generator

class StreamController:
    def __init__(self):
        self.video_volume = 0.0
        self.video_playing = False
        self.video_muted = False
        self.video_running = False
        self.video_fullscreen = False

    async def initialize(self):
        async with async_playwright() as playwright:
            await self.init_browser(playwright)
            self.load_config()

            await self.run()

    async def init_browser(self, playwright):
        # Extension installed manually since using sessions

        user_data_dir = os.path.abspath("stream_controller/profiles/nathan")
        print(user_data_dir)
        self.browser = await playwright.firefox.launch_persistent_context(user_data_dir, headless=False)
        self.page = await self.browser.new_page()

    def load_config(self, config_filepath=os.path.abspath("stream_controller/resources/stream_controller_config.ini")):
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

        url_list = url_generator.fetch_video_urls(self.preset, video_url, black_url_keywords)

        for url in url_list:
            print(f"Loading url")

            self.video_running = False

            try:
                await self.load_url(url)
            except Exception as e:
                print(f"ERROR: {e}")
                continue

            print("Video running...")

            while self.video_running:
                await asyncio.sleep(1)

    async def load_url(self, url):
        await self.page.goto(url)
        
        self.hwnd = self.get_window_handle()

        self.video_element = self.page.locator("video")

        await self.page.locator("body").click()
        await self.toggle_play()
        await self.change_volume(1, volume_amount=1.0)

        self.video_running = True

    async def change_volume(self, direction=1, volume_amount=None):
        if volume_amount is None:
            volume_amount = self.video_volume + float(self.default_config["VOLUME_AMOUNT"]) * direction

        if (volume_amount > 1.0):
            volume_amount = 1.0
        elif (volume_amount < 0.0):
            volume_amount = 0.0

        script = "video_element => video_element.volume={volume_amount}".format(volume_amount=volume_amount)
        await self.video_element.evaluate(script)

        self.video_volume = volume_amount

    async def increase_volume(self):
        await self.change_volume(+1)

    async def decrease_volume(self):
        await self.change_volume(-1)

    async def toggle_mute(self):
        if (self.video_muted):
            await self.video_element.evaluate("video_element => video_element.muted=false;")
            await self.change_volume(volume_amount=1.0)
            self.video_muted = False
        else:
            await self.video_element.evaluate("video_element => video_element.muted=true;")
            self.video_muted = True

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

    async def seek_forward(self):
        await self.seek(+1)

    async def seek_backward(self):
        await self.seek(-1)

    async def toggle_fullscreen(self):
        if self.video_fullscreen:
            # await self.video_element.evaluate('video_element => video_element.mmozCancelFullScreen();')
            await self.page.keyboard.press('Escape')
            self.video_fullscreen = False
        else:
            await self.video_element.evaluate('video_element => video_element.requestFullscreen();')
            self.video_fullscreen = True

    # def next_video(self):
    # def previous_video(self):

    # def skip_intro(self):

    def get_window_handle(self):
        hwnd = ctypes.windll.user32.GetForegroundWindow()

        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
    
        print(f"WINDOW HANDLE: {buf.value}")

        return hwnd

    def check_window_focus(self):
        return self.get_window_handle() == self.hwnd

    def get_window_titles(self):
        titles = []

        EnumWindows = ctypes.windll.user32.EnumWindows
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))

        def foreach_window(hwnd, lParam):
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
            titles.append(buff.value)
            return True

        EnumWindows(EnumWindowsProc(foreach_window), 0)

        return titles

    async def set_window_focus(self):
        print(self.get_window_titles())

        # user32 = ctypes.windll.user32
        # user32.ShowWindow(hwnd, 9)  # SW_RESTORE
        # user32.SetForegroundWindow(hwnd)

if __name__ == "__main__":
    stream_controller = StreamController()
    asyncio.run(stream_controller.initialize())
