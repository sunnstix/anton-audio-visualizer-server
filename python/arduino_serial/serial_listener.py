#!/usr/bin/env python3
import serial
import time
if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyACM1', 9600, timeout=1)
    ser.flush()
    while True:
        #ser.write(b'0000000700ff0000080000000009000000ff0a00')
        try:
            line = ser.readline().decode('utf-8').rstrip()
        except Exception:
            line = ser.readline().decode("hex")
        print(line)