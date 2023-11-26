import serial
import threading
import time

from typing import Tuple
from serial.tools import list_ports


def get_serial_ports():
    ports = list_ports.comports()
    return [port.device for port in ports]


class MySerial(threading.Thread):
    def __init__(self, port: str, baudrate: int, timeout: float = 0.5):
        super(MySerial, self).__init__()
        self._serial: serial.Serial = serial.Serial(timeout=timeout)
        self._recv_cb = None
        self._active = False
        self._port = port
        self._baudrate = baudrate

    @property
    def port(self):
        return self._port

    def open(self):
        self._serial.port = self._port
        self._serial.baudrate = self._baudrate
        self._serial.open()

    def set_receive_callback(self, cb):
        self._recv_cb = cb

    def send(self, data: bytes):
        self._serial.write(data)

    def stop(self):
        self._active = False
        self.join()
        self._serial.close()

    def run(self):
        self._active = True
        while self._active:
            data = self._serial.read(1024)
            if data:
                if self._recv_cb:
                    self._recv_cb(data)
