import struct
import functools
from abc import ABC, abstractmethod
from lib.model.enums.kinds import Reply_type, Message_type, Device_type, Command_type
from lib.const import power
import datetime

class Message(ABC):
    def __init__(self, type:Message_type=None):
        self.checksum=None
        self.magic=None
        self.mtype:Message_type=type
        self.date_time=None
        return self
    
    def __str__(self):
        dic={i:v for i, v in self.__dict__.items() if not i.startswith("__") and not callable(i) and v is not None}
        return str(dic)
    
    def __repr__(self):
        return str(self.__dict__)

    @staticmethod
    def make_from_data(raw_data:bytes):
        assert raw_data[:2]==b'\xFF\x55'
        type=Message_type(raw_data[2])
        if type==Message_type.Report:
            m=ReportMessage()
        elif type==Message_type.Command:
            m=CommandMessage()
        elif type==Message_type.Reply:
            m=ReplyMessage()
        m.magic=raw_data[:2]
        m.date_time=datetime.datetime.now()
        payload_length=type.getPayloadLength()
        payload=raw_data[3:3+payload_length]
        checksum=raw_data[3+payload_length]
        assert len(raw_data)==3+payload_length+1
        calculated_checksum = functools.reduce(lambda acc, item: (acc + item) & 0xff, payload) ^ 0x44
        assert checksum==calculated_checksum
        m.__parse__(payload)
        return m

    @abstractmethod    
    def __parse__(self, payload:bytes):
        pass

    @abstractmethod    
    def __generate__(self, *args, **kwargs):
        pass

    def generate(self, *args, **kwargs):
        return b'\xFF\x55'+self.__generate__(*args, **kwargs)


class ReportMessage(Message):
    report_mapper={
            "MaxVoltage": "MaxV",
            "MinVoltage": "MinV",
            "MaxAmp": "MaxI",
            "Voltage": "V",
            "Power_factor": "PF",
            "Amp": "I",
            "Temperature": "T",
            "Watt": "E",
            "Watt_hour": "C",
            "Frequency": "F",
            "time": "Time",
            "Price": "€",
            "Backlight": "BL",
            "Reserved": "Reserved",
            "Total_price": "?",
            "USB_D_minus": "D-",
            "USB_D_plus": "D+",
            "device_type": "Type",
            "date_time": "dateTime",
        }
    def __init__(self):
        self.Voltage=None
        self.Amp=None
        self.Watt=None
        self.Watt_hour=None
        self.Price=None
        self.Frequency=None
        self.Power_factor=None
        self.Temperature=None
        self.USB_D_minus=None
        self.USB_D_plus=None
        self.time=None
        self.Backlight=None
        self.Total_price=None
        self.MaxVoltage=None
        self.MinVoltage=None
        self.MaxAmp=None
        self.Reserved=None
        self.mtype= Message_type.Report
        
        self.device_type: Device_type=None
    
    def __parse__(self, payload:bytes):
        assert len(payload)==32
        self.device_type=Device_type(payload[0])
        mapper_array=power[self.device_type.value]
        bytes_count="".join(["{}s".format(i[0]) for i in mapper_array])
        nums=struct.unpack(bytes_count, payload[1:])
        values_dic={name[1]: int.from_bytes(value, "big")/name[2] for name, value in zip(mapper_array, nums)}
        for i, v in values_dic.items():
            if i in ["Hour", "Minute", "Second"]:
                continue
            setattr(self, i, v)
        self.time="{:02.0f}:{:02.0f}:{:02.0f}".format(values_dic["Hour"], values_dic["Minute"], values_dic["Second"])
        try:
            self.Reserved=hex(int(self.Reserved))
            self.Backlight=int(self.Backlight)
        except:
            pass
        return self
    
    # Not implemented
    def __generate__(self):
        raise NotImplementedError

    
class CommandMessage(Message):
    def __init__(self):
        self.device_type: Device_type=None
        self.command_type: Command_type=None
        self.value=None
        self.mtype=Message_type.Command
    
    def __parse__(self, payload:bytes):
        self.device_type, self.command_type, self.value=struct.unpack(">BBi", payload)
        return self
    
    def __generate__(self, device_type:Device_type, command_type:Command_type, value:int):
        dev_bytes=device_type.value.to_bytes(1, "big")
        cmd_bytes=command_type.value.to_bytes(1, "big")
        value_bytes=value.to_bytes(4, "big")
        _type=self.mtype.value.to_bytes(1, "big")
        payload=_type+dev_bytes+cmd_bytes+value_bytes
        checksum=functools.reduce(lambda acc, item: (acc + item) & 0xff, payload) ^ 0x44
        return payload+checksum.to_bytes(1, "big")


class ReplyMessage(Message):
    def __init__(self):
        self.state:Reply_type=None
        self.mtype=Message_type.Reply
    
    def __parse__(self, payload:bytes):
        assert len(payload)==4
        self.state=Reply_type(struct.unpack(">H", payload)[0])
        return self

    # Not implemented
    def __generate__(self):
        raise NotImplementedError

        