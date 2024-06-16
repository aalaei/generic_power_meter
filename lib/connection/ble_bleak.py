
# # import uuid

# CHAR_UUID = uuid.UUID("0000ffe1-0000-1000-8000-00805f9b34fb")
# DEVICE_NAME="UC96_BLE"
# # 3A:4E:A4:D8:C0:48: UC96_BLE
# # UUID="00002A04-0000-1000-8000-00805F9B34FB"
# async def run(loop):
#     address = "3A:4E:A4:D8:C0:48"
#     devices = await BleakScanner.discover()
#     device = list(filter(lambda d: d.name == DEVICE_NAME, devices))
#     if len(device) == 0:
#         raise RuntimeError(f"Failed to find a device name '{DEVICE_NAME}'")

#     address = device[0].address
#     async with BleakClient(address, loop=loop) as client:
#         services = client.services
#         for s in services:
#             print(s)
#             for c in s.characteristics:
#                 if "notify" in c.properties:
#                     print(c.uuid)
#         def cb(sender, data):
#             print(data)
#         await client.start_notify(CHAR_UUID, cb)
#         # client.
#         # pickle.dump(services, open("services.pkl", "wb"))
#         # print(data)
#         # model_number = await client.read_gatt_char(MODEL_NBR_UUID)
#         # print("Model Number: {0}".format("".join(map(chr, model_number))))

# # asyncio.run(main())
# loop = asyncio.get_event_loop()
# loop.run_until_complete(run(loop))
# # services=pickle.load(open("services.pkl", "rb"))

# # print(services)


from lib.connection.generic_connection import Generic_Connection
from lib.exception import BLUETOOTH_NOT_CONNECTED
import asyncio
import threading
from bleak import BleakScanner, BleakClient
 
class BLE_Connection(Generic_Connection):
    def __init__(self, target=None):
        super().__init__(target)
        self.connected:bool=False
        self.client:BleakClient=None
        self.uuid=None
        self.thread=None
        self.stop=False
        self.loop=None
        self.loop=asyncio.get_event_loop()

    
    def sync_call(self, fn, *args, **kwargs):
        # future =asyncio.run_coroutine_threadsafe(fn(*args,**kwargs), self.loop)
        return self.loop.run_until_complete(fn(*args,**kwargs))
        # return future.result(100)
    
    def search(self, dev_name = None):
        return self.sync_call(self._search, dev_name)
    
    def set_target(self, target):
        self.target=target
    
    async def _search(self, dev_name = None):
        devices = await BleakScanner.discover()
        if dev_name is not None:
            devices = list(filter(lambda d: d.name == dev_name, devices))
        if len(devices) == 0:
            raise RuntimeError(f"Failed to find a device name '{dev_name}'")
        return devices[0]
    
    async def connect_and_process(self):
        self.client=BleakClient(self.target, loop=self.loop)
        try:
            r=await self.client.connect()
        except Exception as e:
            print(e)
        self.connected=True
        
        for s in self.client.services:
            for c in s.characteristics:
                if "notify" in c.properties and "write" in c.properties:
                    self.uuid=c.uuid
                    break
        
        async def ccb(sender, data):
            for cb in self.cb:
                cb(data)
        
        await self.client.start_notify(self.uuid, ccb)
        return r

    def connect(self, ev_cb=None):
        if self.connected:
            return True
        self.sync_call(self.connect_and_process)
        return True

    def disconnect(self):
        if not self.connected:
            return
        self.sync_call(self.client.disconnect)
        self.connected=False
        return True

    def send(self, data):
        if not self.connected:
            raise BLUETOOTH_NOT_CONNECTED
        return self.sync_call(self.client.write_gatt_char,self.uuid, data)

    def receive(self):
        raise Exception("Not implemented")

    def __del__(self):
        print("calling me")
        self.disconnect()
        
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return self.disconnect()

    

    
