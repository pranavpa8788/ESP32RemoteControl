import serial
import io
import time

ser = serial.serial_for_url('COM5', 9600, timeout=10)
time.sleep(2)
sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
time.sleep(2)
sio.write("hello\n")
sio.flush() # it is buffering. required to get the data out *now*
time.sleep(2)
hello = sio.readline()
print(repr(hello))
