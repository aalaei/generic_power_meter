

from lib.connection.generic_connection import Generic_Connection
from lib.exception import BLUETOOTH_NOT_CONNECTED, BLUETOOTH_NO_ADAPTER_FOUND
import threading
import time
import simplepyble
 
class SBLE_Connection(Generic_Connection):
    def __init__(self, target=None):
        super().__init__(target)
        self.connected:bool=False
        self.uuid=None
        self.thread=None
        self.adapters = simplepyble.Adapter.get_adapters()
        if len(self.adapters) == 0:
            raise BLUETOOTH_NO_ADAPTER_FOUND
        self.init_adapter()
    def init_adapter(self):
        adapter = self.adapters[0]
        adapter.set_callback_on_scan_start(self.on_scan_start)
        adapter.set_callback_on_scan_stop(self.on_scan_stop)
        adapter.set_callback_on_scan_found(self.on_scan_found)

    def on_scan_start(self):
        print("Starting scan...")
    
    def on_scan_stop(self):
        print("Scan complete.")
    
    def on_scan_found(self, peripheral):
        print(f"Found {peripheral.identifier()} [{peripheral.address()}]")
        if self.t_name is not None and peripheral.identifier() == self.t_name:
            self.target=peripheral        
            self.adapters[0].scan_stop()

    
    def set_target(self, target):
        self.target=target
    
    def search(self, dev_name = None, timeout=10):
        self.t_name=dev_name
        adapter=self.adapters[0]
        adapter.scan_start()#(timeout*1000)
        cnt=0
        while adapter.scan_is_active():
            time.sleep(0.1)
            cnt+=1
            if cnt>timeout*10:
                adapter.scan_stop()
                break
        peripherals = adapter.scan_get_results()
        # for i, peripheral in enumerate(peripherals):
        #     print(f"{i}: {peripheral.identifier()} [{peripheral.address()}]")
        if dev_name is not None:
            peripherals = list(filter(lambda d: d.identifier() == dev_name, peripherals))
        if len(peripherals) == 0:
            raise RuntimeError(f"Failed to find a device name '{dev_name}'")
        return peripherals[0]
    
    def connect_and_process(self):
        peripheral=self.target
        try:
            peripheral.connect()
        except Exception as e:
            print(e)
        self.connected=True
        services = peripheral.services()
        for service in services:
            for characteristic in service.characteristics():
                if (characteristic.can_notify() and
                    characteristic.can_write_command() and characteristic.can_write_request()):
                    self.uuid= (service.uuid(), characteristic.uuid())
                    break
        
        return True

    def connect(self, ev_cb=None):
        if self.connected:
            return True
        if not self.connect_and_process():
            return False
        
        def ccb(data):
            print(data)
            for cb in self.cb:
                cb(data)
        
        contents = self.target.notify(self.uuid[0], self.uuid[1], ccb)
        return True

    def disconnect(self):
        if not self.connected:
            return
        self.target.disconnect()
        self.connected=False
        return True

    def send(self, data):
        if not self.connected:
            raise BLUETOOTH_NOT_CONNECTED
        return self.target.write_request(self.uuid[0], self.uuid[1], data)

    def receive(self):
        raise Exception("Not implemented")

    def __del__(self):
        self.disconnect()
        self.target.disconnect()
        
    def __enter__(self):
        return self


