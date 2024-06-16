class DEV_TYPE_NOT_SET(Exception):
    def __init__(self) -> None:
        super().__init__("Device type not set")

class BLUETOOTH_EXCEPTION(Exception):
    def __init__(self) -> None:
        super().__init__("Bluetooth exception")

class BLUETOOTH_NOT_CONNECTED(BLUETOOTH_EXCEPTION):
    def __init__(self) -> None:
        super().__init__("Bluetooth not connected")
class BLUETOOTH_NO_ADAPTER_FOUND(BLUETOOTH_EXCEPTION):
    def __init__(self) -> None:
        super().__init__("Bluetooth adapter not found")


class NAME_ALREADY_EXISTS(Exception):
    def __init__(self) -> None:
        super().__init__("Name already exists")
