from enum import Enum
payload_mapper={"Report": 32, "Reply": 4, "Command": 6}
class Message_type(Enum):
    Report=1
    Reply=2
    Command=0x11
    
    def getPayloadLength(self):
        return payload_mapper[self.name]

    def __str__(self):
        return self.name

class Device_type(Enum):
    AC_Meter=1
    DC_Meter=2
    USB_Meter=3

    def __str__(self):
        return self.name

class Command_type(Enum):
    NoneN=0x0
    Reset_power=0x1
    Reset_capacity=0x2
    Reset_time=0x3
    Reset_all=0x5
    Navigation_Plus=0x11
    Navigation_Minus=0x12
    Backlight_time=0x21 #0 to 60
    Price=0x22 # 1 to 999999
    Setup=0x31
    Enter=0x32
    Navigation_Plus_USB=0x33
    Navigation_Minus_USB=0x34

    def __str__(self):
        return self.name
class Reply_type(Enum):
    OK= 0x201
    Unsupported = 0x203

    def __str__(self):
        return self.name
