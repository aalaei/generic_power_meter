from abc import ABC, abstractmethod

class Generic_Connection(ABC):
    def __init__(self, target):
        self.target = target
        self.cb=[]
        self.connected=False
        self.thread=None
        
    def add_cb(self, cb):
        self.cb.append(cb)
    
    def remove_cb(self, index=None):
        self.cb.pop(index)

    @abstractmethod
    def connect(self, ev_cb=None):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def send(self, data):
        pass

    @abstractmethod
    def receive(self):
        pass

    