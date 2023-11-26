import socket
import threading
import time

from typing import Tuple


class MyUDP(threading.Thread):
    def __init__(self):
        super(MyUDP, self).__init__()
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.settimeout(1)
        self._recv_cb = None
        self._active = False

    def set_receive_callback(self, cb):
        self._recv_cb = cb

    def bind_to(self, ip: str, port: int):
        self._socket.bind((ip, port))

    def send(self, target: Tuple[str, int], data: bytes):
        self._socket.sendto(data, target)

    def stop(self):
        self._active = False
        self.join()

    def run(self):
        self._active = True
        while self._active:
            try:
                data, source = self._socket.recvfrom(1024)
                if self._recv_cb is not None:
                    self._recv_cb(source, data)
            except socket.timeout:
                pass
