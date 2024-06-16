ac_power=[(3, "Voltage", 10),(3, "Amp", 1000), (3,"Watt", 10), (4, "Watt_hour", 100), (3, "Price", 100),
                (2, "Frequency", 10), (2, "Power_factor", 1000), (2, "Temperature", 1), (2, "Hour", 1),
                (1, "Minute", 1),(1, "Second", 1), (1, "Backlight", 1), (4, "Reserved", 1)]
    
dc_power=[(3, "Voltage", 10),(3, "Amp", 1000), (3,"Watt", 10), (4, "Watt_hour", 100), (3, "Price", 100),
            (4, "Total_price", 1), (2, "Temperature", 1), (2, "Hour", 1),(1, "Minute", 1),
            (1, "Second", 1), (1, "Backlight", 1), (4, "Reserved", 1)]
usb_power=[(3, "Voltage", 100),(3, "Amp", 100), (3,"Watt_hour", 1000), (4, "Watt_hour", 100), (2, "USB_D_minus", 100),
            (2, "USB_D_plus", 100), (2, "Temperature", 1), (2, "Hour", 1),(1, "Minute", 1),
            (1, "Second", 1),(1, "Backlight", 1), (2, "MaxVoltage", 100), (2, "MinVoltage", 100),
            (2, "MaxAmp", 100), (1, "Reserved", 1)]
assert sum([i[0] for i in dc_power]) ==31
assert sum([i[0] for i in ac_power]) ==31
assert sum([i[0] for i in usb_power]) ==31

power={
    1: ac_power,
    2: dc_power,
    3: usb_power
}
