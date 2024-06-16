
from typing import List
from lib.model.enums.kinds import Message_type
from lib.model.message import Message

class MessageParser:
    def __init__(self) -> None:
        pass
    @staticmethod
    def parse_datas(raw_data:bytes) -> List[Message]:
        ind=0
        messages=[]
        while ind<len(raw_data):
            assert raw_data[:2]==b'\xFF\x55'
            message_type=Message_type(raw_data[2])
            payload_length=message_type.getPayloadLength()
            # payload=raw_data[3:3+payload_length]
            # checksum=raw_data[3+payload_length]
            m=Message.make_from_data(raw_data[ind:ind+3+payload_length+1])
            ind+=payload_length+4
            messages.append(m)
        return messages
