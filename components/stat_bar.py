from textual.app import ComposeResult
from textual.containers import HorizontalScroll
from textual.widgets import Static, Label, Digits
from lib.model.enums.kinds import Device_type
from textual.reactive import reactive

class ValueDisplay(Static):
    value=reactive(None)


    def __init__(self,ivalue, *args, **kwargs):
        self.ivalue=ivalue
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield Label(self.name)
        yield Digits(self.ivalue, id=f"value_{self.id}")
    
    def watch_value(self, value):
        if value is None:
            return
        self.query_one(f"#value_{self.id}").update(str(value))

class PowerStats(Static):
    values=reactive({})
    def compose(self) -> ComposeResult:
        # yield Horizontal(id="power_stats_container")
        with HorizontalScroll(id="power_stats_container"):
            # yield Placeholder(id="p1")
            yield ValueDisplay("-", name="Voltage")
        #   
        
        self.device_type: Device_type=None
    def watch_values(self, values):
        for k, v in values.items():
            self.query_one(f'#{k.replace("-", "_").replace("+", "__")}').value=v
