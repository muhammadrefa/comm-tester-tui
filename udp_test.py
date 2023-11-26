#!/usr/bin/env python3

import time

from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Button, Label, Input

from mylib.comm_test import Sidebar, DataLog, SendDataBar, InformationBox, CommTestApp

from typing import Tuple
from mylib.myudp import MyUDP


class UDPSidebar(Sidebar):
    def compose(self) -> ComposeResult:
        yield ScrollableContainer(
            Label("Bind IP"),
            Input(placeholder="Bind IP", id="bind_ip", value="0.0.0.0"),
            Label("Bind port"),
            Input(placeholder="Bind port", id="bind_port", value="8000"),
            Label("Target IP"),
            Input(placeholder="Target IP", id="target_ip"),
            Label("Target port"),
            Input(placeholder="Target port", id="target_port"),
            Button("Start", id="btn_start_bind", variant="primary"),
            Button("Stop", id="btn_stop_bind", variant="error")
        )


class UdpTestApp(CommTestApp):
    udp_socket: MyUDP = None

    def compose(self) -> ComposeResult:
        yield UDPSidebar(classes="sidebar")
        yield DataLog(classes="datalog", id="datalog")
        yield InformationBox(classes="information-box")
        yield SendDataBar(classes="send-data-bar")

    def bind_start(self):
        # Disable inputs
        self.query_one('#bind_ip').disabled = True
        self.query_one('#bind_port').disabled = True
        self.query_one('#target_ip').disabled = True
        self.query_one('#target_port').disabled = True
        self.add_class("listening")

        # Bind
        bind_ip = self.query_one('#bind_ip').value
        bind_port = int(self.query_one('#bind_port').value)

        # Start UDP thread
        try:
            self.udp_socket = MyUDP()
            self.udp_socket.bind_to(bind_ip, bind_port)
            self.udp_socket.set_receive_callback(self.udp_received)
            self.udp_socket.start()

            self.write_to_log(f"Listening to [magenta]\\[{bind_ip}:{bind_port}][/magenta]")
        except Exception as e:
            self.write_to_log(f"[red]{e}[/red]")
            # Enable inputs
            self.remove_class("listening")
            self.query_one('#bind_ip').disabled = False
            self.query_one('#bind_port').disabled = False
            self.query_one('#target_ip').disabled = False
            self.query_one('#target_port').disabled = False

    def bind_stop(self):
        # Stop UDP thread
        try:
            self.udp_socket.stop()
        except AttributeError:
            pass

        # Enable inputs
        self.remove_class("listening")
        self.query_one('#bind_ip').disabled = False
        self.query_one('#bind_port').disabled = False
        self.query_one('#target_ip').disabled = False
        self.query_one('#target_port').disabled = False

        self.write_to_log(f"Stop listening")

    def send_data(self):
        # Target and Data
        target_ip = self.query_one('#target_ip').value
        target_port = int(self.query_one('#target_port').value)
        data = self.query_one("#data_to_send").value

        # Send
        try:
            self.udp_socket.send((target_ip, target_port), data.encode())
            self.write_comm_log(f"{target_ip}:{target_port}", False, data)
        except AttributeError:
            pass

    def udp_received(self, source: Tuple[str, int], data: bytes):
        self.write_comm_log(f"{source[0]}:{source[1]}", True, data.decode(errors='ignore'))


if __name__ == "__main__":
    app = UdpTestApp()
    app.run()
