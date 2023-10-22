import serial
import asyncio

async def read_serial(ser):
    while True:
        data = await loop.run_in_executor(None, ser.read, 100)
        if data:
            print(data.decode(), end='')

async def count():
    while True:
        await asyncio.sleep(1)
        print("YO")

async def main():
    ser = serial.Serial('COM5', 9600)
    try:
        await asyncio.gather(
            read_serial(ser),
            count()
        )
    except KeyboardInterrupt:
        print("YO")
        print("Serial communication interrupted.")
    finally:
        ser.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
