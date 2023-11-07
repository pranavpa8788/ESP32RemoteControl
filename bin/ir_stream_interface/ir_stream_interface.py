import asyncio
import os
import configparser

from serial_asyncio import open_serial_connection
from stream_controller.stream_controller import StreamController

class IRStreamInterface:
    def __init__(self):
        self.stream_controller = StreamController()
        self.load_config()

    def load_config(self, config_filepath=os.path.abspath("ir_stream_interface/resources/ir_stream_interface_config.ini"), pio_ini_filepath = os.path.abspath("ir_receiver/platformio.ini")):
        config = configparser.ConfigParser()
        config.read(config_filepath)

        remote = config["DEFAULT"]["REMOTE"]
        self.remote_config = config[remote]

        pio_config = configparser.ConfigParser()
        pio_config.read(pio_ini_filepath)

        self.pio_config = pio_config["env:esp32dev"]

    async def init_stream_controller(self):
        print("Initializing stream controller")

        await self.stream_controller.initialize()

    async def read_serial_data(self):
        self.reader, self.writer = await open_serial_connection(url=self.pio_config["upload_port"], baudrate=self.pio_config["monitor_speed"])

        while True:
            print("Running read serial data")

            command_data = ""

            while len(command_data) < 8:
                data = await self.reader.read(1)  # Read a single byte
                char = data.decode()
                command_data += char

            print(f"{command_data=}")

            if (len(command_data) == 8) and self.stream_controller.video_running is True:
                await self.execute_command(command_data)

            await asyncio.sleep(0.1)

    async def execute_command(self, command_data):
        if (command_data in self.remote_config.keys()):
            command = self.remote_config[command_data]
            command_function = getattr(self.stream_controller, command.lower(), None)

            await command_function()
        else:
            self.reader.flush()
            print("command data not found")
            

    async def run(self):
        await asyncio.gather(self.read_serial_data(), self.init_stream_controller())
        # self.stream_controller.video_running = True
        # await asyncio.gather(self.read_serial_data())

if __name__ == "__main__":
    ir_stream_interface = IRStreamInterface()
    asyncio.run(ir_stream_interface.run())
