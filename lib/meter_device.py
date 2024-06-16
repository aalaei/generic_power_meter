
from lib.model.message import Message, ReportMessage, CommandMessage, ReplyMessage
from lib.model.messages import MessageParser
from lib.connection import Generic_Connection
from lib.model.enums.kinds import Command_type, Message_type
from lib.model.enums.kinds import Device_type
from lib.exception import DEV_TYPE_NOT_SET, NAME_ALREADY_EXISTS
from typing import List

class Meterdevice:
    def __init__(self, connection:Generic_Connection) -> None:
        self.connection:Generic_Connection=connection
        self.connection.add_cb(self.__on_datas__)
        self.message_parser:MessageParser=MessageParser()
        self.device_type:Device_type=None
        self.cb=[]
    
    def add_cb(self, cb, filter: List[Message_type], name=None):
        if name is None:
            name=cb.__name__
        names={name for name, _, _ in self.cb}
        if name in names:
            raise NAME_ALREADY_EXISTS()
        self.cb.append((name, filter, cb))
    
    def get_cbs(self):
        return { i:{"name":name, "filter":filter, "cb":cb}
            for i,(name, filter, cb) in enumerate(self.cb)
        }

    def remove_cb_by_name(self, _name=None):
        self.cb=[(name, filter, cb) for name, filter, cb in self.cb if name!=_name]
    
    def remove_cb_by_index(self, index=None):
        self.cb.pop(index)
    
    def __on_datas__(self, data):
        ms=self.message_parser.parse_datas(data)
        for m in ms:
            self.__on_data__(m)
        
    def set_device_type(self, device_type:Device_type):
        self.device_type=device_type
    
    def __on_data__(self, data:Message):
        for _, filter, cb in self.cb:
            if data.mtype in filter:
                cb(data)
        if isinstance(data, ReportMessage):
            self.__on_report__(data)
        elif isinstance(data, CommandMessage):
            self.__on_command__(data)
        elif isinstance(data, ReplyMessage):
            self.__on_reply__(data)
    
    def __on_report__(self, data:ReportMessage):
        self.device_type=data.device_type
    
    def __on_command__(self, data:CommandMessage):
        self.device_type=data.device_type

    def __on_reply__(self, data:ReplyMessage):
        print(data)
        pass

    def connect(self, ev_cb=None):
        if self.connection.connect(ev_cb):
            return True
    
        raise Exception("Connection failed")
    
    def disconnect(self):
        return self.connection.disconnect()
    
    def is_connected(self):
        return self.connection.connected
    
    def raw_send(self, data):
        self.connection.send(data)
    
    def send_command(self, cmd_type:Command_type, value: int=0):
        if self.device_type is None:
            raise DEV_TYPE_NOT_SET
        cmd= CommandMessage().generate(self.device_type, cmd_type, value)
        self.raw_send(cmd)

    def __del__(self):
        self.disconnect()
