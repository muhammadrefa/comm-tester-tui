#!/usr/bin/env python3

import time

from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Button, Label, Input, Select

from mylib.comm_test import Sidebar, DataLog, SendDataBar, InformationBox, CommTestApp

from typing import Tuple
from mylib.myserial import MySerial, get_serial_ports


class SerialSidebar(Sidebar):

    def compose(self) -> ComposeResult:
        yield ScrollableContainer(
            Label("Serial port"),
            Select([], id="cmb_serial_port", allow_blank=True, prompt="Refresh"),
            # Input(placeholder="Serial port", id="serial_port", value=""),
            Label("Baud rate"),
            Input(placeholder="Baud rate", id="baud_rate", value="9600"),
            Button("Start", id="btn_start_bind", variant="primary"),
            Button("Stop", id="btn_stop_bind", variant="error")
        )


class SerialTestApp(CommTestApp):
    serial_comm: MySerial = None

    def compose(self) -> ComposeResult:
        yield SerialSidebar(classes="sidebar")
        yield DataLog(classes="datalog", id="datalog")
        yield InformationBox(classes="information-box")
        yield SendDataBar(classes="send-data-bar")

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed):
        if event.select.value is None:
            self.query_one("#cmb_serial_port").set_options([(p, p) for p in get_serial_ports()])
            # self.query_one('#btn_start_bind').disabled = True
            if self.has_class("port-selected"):
                self.remove_class("port-selected")
        else:
            # self.query_one('#btn_start_bind').disabled = False
            if not self.has_class("port-selected"):
                self.add_class("port-selected")

        self.query_one("#log").write(f"{self.classes}")

    def bind_start(self):
        # Disable inputs
        self.query_one('#cmb_serial_port').disabled = True
        self.query_one('#baud_rate').disabled = True
        self.add_class("listening")

        # Bind
        port = self.query_one('#cmb_serial_port').value
        if port is None:
            port = self.query_one('#serial_port').value
        baud = int(self.query_one('#baud_rate').value)

        # Start serial thread
        try:
            self.serial_comm = MySerial(port, baud)
            self.serial_comm.open()
            self.serial_comm.set_receive_callback(self.serial_received)
            self.serial_comm.start()

            self.write_to_log(f"Serial port [magenta]\\[{port}][/magenta] opened (baudrate {baud})")
        except Exception as e:
            self.write_to_log(f"[red]{e}[/red]")
            # Enable inputs
            self.remove_class("listening")
            self.query_one('#cmb_serial_port').disabled = False
            self.query_one('#baud_rate').disabled = False

    def bind_stop(self):
        # Stop Serial thread
        try:
            self.serial_comm.stop()
        except AttributeError:
            pass

        # Enable inputs
        self.remove_class("listening")
        self.query_one('#cmb_serial_port').disabled = False
        self.query_one('#baud_rate').disabled = False

        self.write_to_log(f"Serial port [magenta]\\[{self.serial_comm.port}][/magenta] closed")

    def send_data(self):
        # Target and Data
        data = self.query_one("#data_to_send").value

        # Send
        try:
            self.serial_comm.send(data.encode())
            self.write_comm_log(self.serial_comm.port, False, data)
        except AttributeError:
            pass

    def serial_received(self, data: bytes):
        self.write_comm_log(self.serial_comm.port, True, data.decode(errors='ignore'))


if __name__ == "__main__":
    app = SerialTestApp()
    app.run()
