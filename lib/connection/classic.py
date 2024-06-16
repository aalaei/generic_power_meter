import socket
import threading
from lib.connection.generic_connection import Generic_Connection
from lib.exception import BLUETOOTH_NOT_CONNECTED
class Classic_BConnection(Generic_Connection):
    BUFF_SIZE=1024
    def __init__(self, target):
        super().__init__(target)
        self.sock:socket.socket = None 
        self.connected=False
        self.thread=None
        self.stop=False

    def connect(self, ev_cb=None):
        if self.connected:
            return True
        if ev_cb is None:
            return self.__connect__()
        else:
            t=threading.Thread(target=self.__connect__, args=(ev_cb,))
            t.start()
            return None

    def __connect__(self, ev_cb=None):
        try:
            self.sock=socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
            # self.sock.settimeout(1)
            self.sock.connect((self.target, 1))
            self.connected=True
            self.thread=threading.Thread(target=self.__receive__)
            self.thread.start()
            if ev_cb is not None:
                ev_cb(True)
            return True
        except Exception as e:
            print(e)
            # raise e
            if ev_cb is not None:
                ev_cb(False)
            return False

    def disconnect(self):
        if not self.connected:
            return
        self.stop=True
        self.thread.join()
        self.sock.close()
        self.connected=False
        return True

    def send(self, data):
        if not self.connected:
            raise BLUETOOTH_NOT_CONNECTED
        self.sock.send(data)

    def receive(self, buff_size=None):
        if not self.connected:
            raise BLUETOOTH_NOT_CONNECTED
        if buff_size is None:
            buff_size=self.BUFF_SIZE
        return self.sock.recv(buff_size)

    def __receive__(self):
        while self.connected and (not self.stop):
            try:
                data=self.receive()
                for cb in self.cb:
                    cb(data)
            except Exception as e:
                print("Error receiving data")
                pass
        self.connected=False
        self.stop=False

    def __del__(self):
        self.disconnect()
        self.sock.close()
    
    