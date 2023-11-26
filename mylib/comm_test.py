import os
import time

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer, VerticalScroll, HorizontalScroll, Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Header, Footer, Button, Static, Label, Input, Checkbox, RichLog


class Sidebar(Static):
    def on_mount(self):
        self.border_title = "Configuration"


class DataLog(Static):
    def on_mount(self):
        self.border_title = "Log"

    def compose(self) -> ComposeResult:
        yield Vertical(
            RichLog(id="log", highlight=False, markup=True),
            Horizontal(
                # Checkbox("As HEX"),
                Checkbox("Timestamp", id="chk_timestamp"),
                Button("Clear", id="btn_clearlog", variant="error"),
                id="log_ctrl"
            )
        )

    def on_button_pressed(self, event: Button.Pressed):
        btn_id = event.button.id
        if btn_id == "btn_clearlog":
            self.query_one("#log").clear()


class SendDataBar(Static):
    def on_mount(self):
        self.border_title = "Data"

    def compose(self) -> ComposeResult:
        yield ScrollableContainer(
            Horizontal(
                Input(placeholder="Data to send...", id="data_to_send"),
                Button("Send", id="btn_send", variant="success"),
                # Button("Stop", id="btn_stop", variant="error")
            ),
            # Horizontal(
            #     Checkbox("As HEX"),
            #     Checkbox("Send every (secs.)"),
            #     Input(placeholder="Secs...", id="send-interval")
            # )
        )


class InformationBox(Static):
    def on_mount(self):
        self.border_title = "Information"

    def compose(self) -> ComposeResult:
        yield Label(id="info")


class CommTestApp(App):
    CSS_PATH = f"{os.path.dirname(os.path.abspath(__file__))}/comm_test.tcss"

    def on_button_pressed(self, event: Button.Pressed):
        btn_id = event.button.id
        if btn_id == "btn_start_bind":
            self.bind_start()
        elif btn_id == "btn_stop_bind":
            self.bind_stop()
        elif btn_id == "btn_send":
            self.send_data()
        # elif btn_id == "btn_stop":
        #     self.query_one("#log").write("Stop")

    def bind_start(self):
        pass

    def bind_stop(self):
        pass

    def send_data(self):
        pass

    def write_to_log(self, text: str):
        self.query_one("#log").write(text)

    def write_comm_log(self, source: str, is_receive: bool, data: str):
        timestamp = str()
        if self.query_one('#chk_timestamp').value:
            timestamp = f"[cyan]\\[{time.strftime('%H:%M:%S')}][/cyan] "
        self.write_to_log(f"{timestamp}[magenta]\\[{source}][/magenta] [green]{'->' if is_receive else '<-'}[/green] {data}")
