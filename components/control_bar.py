from textual.app import ComposeResult
from textual.widgets import Input, Button, Static, Select
from lib.model.enums.kinds import Command_type

class ControlBar(Static):
    mapper={
        Command_type.Reset_power: ("Clear Energy", "warning"),
        Command_type.Reset_capacity: ("Clear Capacity", "warning"),
        Command_type.Reset_time: ("Clear Time", "warning"),
        Command_type.Reset_all: ("Reset All", "error"),
        Command_type.Navigation_Plus: ("+", "primary"),
        Command_type.Navigation_Minus: ("-", "primary"),
        Command_type.Backlight_time: ("Backlight Time", "default"),
        Command_type.Price: ("Price", "default"),
        Command_type.Setup: ("Setup", "default"),
        Command_type.Enter: ("Enter", "success"),
        Command_type.Navigation_Plus_USB: ("+", "primary"),
        Command_type.Navigation_Minus_USB: ("-", "primary")
    }
    def compose(self) -> ComposeResult:
        
        vals=["V","I", "T", "W", "D-", "D+"]
        
        yield Select(id="select_var", options=[(k, k) for k in vals], prompt="V", allow_blank= False)
        yield Input(placeholder="Value to send", id="value_to_send", type="integer", value="0", max_length=10)
        for k, v in self.mapper.items():
            yield Button(v[0], id=f"control_{k.name}", variant=v[1], classes="control_button")
    