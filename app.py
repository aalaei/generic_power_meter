from textual.app import App, ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.widgets import TabbedContent, Header, Button, LoadingIndicator, RichLog, Select, Footer
from lib.meter_device import Meterdevice

from lib.connection import Classic_BConnection, SBLE_Connection
from lib.model.enums import Device_type, Command_type, Message_type
from lib.model.message import Message, ReportMessage
from textual import on
import threading
import queue
from components import PowerStats, ControlBar, ValueDisplay, StatPlot


class BluetoothApp(App):
    CSS_PATH = "app.css"
    BINDINGS = [
        ("q", "quit", "quit"),
        ("c", "connect", "connect"),
        ("x", "disconnect", "disconnect"),
        ("d", "toggle_dark_mode", "Toggle dark mode")
    ]

   
    def __on_report_data__(self, data:ReportMessage):
        
        self.device_type: Device_type=None
        
        self.last_report={}
        for k, v in data.__dict__.items():
            if v is not None and (k not in ["magic", "mtype"]):
                self.last_report[ReportMessage.report_mapper.get(k)]=v
                if ReportMessage.report_mapper.get(k)=="I":
                    self.last_report["W"]=self.last_report["V"]*self.last_report["I"]
        # self.last_report={report_mapper.get(k):v for k, v in data.__dict__.items() if v is not None and (k not in ["magic", "mtype"])}
        # self.update_timer.reset()
        self.update_timer.resume()
        x=str(data)
        self.my_log(x)
        print(data)
    def my_log(self, data):
        self.query_one("#log").write(data)

    def update(self):
        plt=self.query_one(StatPlot)
        if self.last_report_set is None:
            if self.last_report["Type"]==Device_type.USB_Meter:
                self.query_one(ControlBar).query_one("#control_Navigation_Plus").remove()
                self.query_one(ControlBar).query_one("#control_Navigation_Minus").remove()
            else:
                self.query_one(ControlBar).query_one("#control_Navigation_Plus_USB").remove()
                self.query_one(ControlBar).query_one("#control_Navigation_Minus_USB").remove()
            
        self.update_timer.pause()
        if self.last_report is None:
            return
        container=self.query_one("#power_stats_container")
        restricted_last_report=self.last_report.copy()
        del restricted_last_report["dateTime"]
        if self.last_report_set is None or (not set(self.last_report_set).__eq__(set(self.last_report.keys()))):   
            plt.add_point(self.last_report, clean=True)
            self.last_report_set=set(self.last_report.keys())
            for a in container.query(ValueDisplay):
                a.remove()
            for k, v in restricted_last_report.items():
                container.mount(ValueDisplay(id=k.replace("-", "_").replace("+", "__"), name=k, ivalue=str(v)))
        else:
            plt.add_point(self.last_report, clean=False)
            self.query_one(PowerStats).values=restricted_last_report


    def __init__(self):
        classic_uuid='3B:4E:A4:D8:C0:48'
        con=Classic_BConnection(classic_uuid)
        # name="UC96_BLE"
        # con=SBLE_Connection()
        # adr=con.search(name)
        # con.set_target(adr)
        self.dev=Meterdevice(con)
        self.queue=queue.Queue()
        self.last_report: dict=None
        self.last_report_set:set= None
        self.dev.add_cb(self.__on_report_data__, [Message_type.Report])
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        yield LoadingIndicator(name="loading", id="loading")
        with Container():
            yield PowerStats(id="power_stats")
            yield ControlBar(id="control_bar")
            with TabbedContent("Visual", "Logs"):
                yield StatPlot(id="plot")
                with ScrollableContainer():
                    yield RichLog(highlight=True, markup=True, id="log")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_name=str(event.button.id)
        if btn_name.startswith("control_"):
            btn_name=btn_name.replace("control_", "")
            cmd=Command_type[btn_name]
            value=int(self.query_one("#value_to_send").value)
            self.dev.send_command(cmd, value)

    def on_mount(self):
        self.query_one("#loading").add_class("hidden")
        self.query_one("Header").query_one("HeaderIcon").icon="?"
        self.update_timer=self.set_interval(1/100, self.update, pause=True)
        self.action_connect()
        
    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        self.query_one(StatPlot).left_variable=str(event.value)


    def wrap_fn(self, cb, fn, *args, **kwargs):
        try:
            x=fn(*args, **kwargs)
            cb(x, fn)
            return x
        except Exception as e:
            print(e)
            cb(None, fn)
            return None
        
    def call_loading(self, fn, *args, **kwargs):
        self.query_one("#loading").remove_class("hidden")
        args=(self.finshed_loading,fn,)+args
        t=threading.Thread(target=self.wrap_fn, args=args, kwargs=kwargs)
        t.start()
  
    def finshed_loading(self, done, fn):
        fn_name=fn.__qualname__.split(".")[-1]
        message="Done" if done else "Error"
        if fn_name=="connect":
            message="[b]Connected[/b] successfully" if done else "[b]Failed[/b] to connect"
            if done:
                self.query_one("Header").query_one("HeaderIcon").icon="⬤"
        elif fn_name=="disconnect":
            message="[b]Disconnected[/b] successfully" if done else "[b]Failed[/b] to disconnect"
            if done:
                self.query_one("Header").query_one("HeaderIcon").icon="◯"
        self.query_one("#loading").add_class("hidden")
        self.notify(
            message,
            title="Bluetooth Connection",
            severity="information" if done else "error",
            timeout=3
        )
        return done
    
    def action_connect(self):
        self.call_loading(self.dev.connect)
        self.my_log("Connected")
        
    def action_disconnect(self):
        self.call_loading(self.dev.disconnect)
        self.my_log("Disconnected")
    
    
    def on_unmount(self):
        self.dev.disconnect()
    

    def action_toggle_dark_mode(self):
        self.dark = not self.dark


if __name__ == "__main__":
    app=BluetoothApp()
    app.run()