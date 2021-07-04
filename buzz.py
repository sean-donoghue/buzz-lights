''' Class for controlling the buzzer lights on PS2 Buzz! controllers '''

import pywinusb.hid as hid

# Vendor & Product IDs for Buzz controllers
vid = 0x054C
pid = 0x1000

# Preset buffers for all lights on & all lights off
buffers = {
    'on':   [0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x00],
    'off':  [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
}

class Buzz(object):
    def __init__(self):
        ''' Connects to Buzz controllers and sets up default values '''
        self.device = hid.HidDeviceFilter(
            vendor_id=vid, product_id=pid).get_devices()[0]
        self.device.open()
        self.set_handler(self.handler)
        self.out_report = self.device.find_output_reports()[0]
        self.buffer = buffers['off'].copy()
        self.data = [0, 0, 0, 0, 0, 240]
        self.data_changed = False
        self.send_buffer()
    

    def handler(self, data: hid.helpers.ReadOnlyList) -> None:
        ''' Records input data and marks the saved data as changed '''
        self.data = data
        self.data_changed = True


    def set_handler(self, handler) -> None:
        ''' Allowed the default data handler to be overridden '''
        self.device.set_raw_data_handler(handler)


    def send_buffer(self) -> None:
        ''' Writes the buffer currently saved in memory to the output report '''
        self.out_report.set_raw_data(self.buffer)
        self.out_report.send()


    def light_none(self) -> None:
        ''' Turns off all of the buzzer lights '''
        self.buffer  = buffers['off'].copy()
        self.send_buffer()


    def light_all(self) -> None:
        ''' Turns on all of the buzzer lights '''
        self.buffer  = buffers['on'].copy()
        self.send_buffer()


    def light_one(self, light: int) -> None:
        ''' Only lights a specified buzzer light '''
        self.buffer = buffers['off'].copy()
        if light > 0 and light < 5:
            self.buffer[light+1] = 0xFF
        self.send_buffer()
    

    def light_some(self, lights: list) -> None:
        ''' Only lights specified buzzer lights '''
        self.buffer = buffers['off'].copy()
        for light in [l for l in lights if l > 0 and l < 5]:
            self.buffer[light+1] = 0xFF
        self.send_buffer()


    def light(self, light: int) -> None:
        ''' Turn on a specified buzzer light '''
        if light > 0 and light < 5:
            self.buffer[light+1] = 0xFF
        self.send_buffer()


    def unlight(self, light: int) -> None:
        ''' Turn off a specified buzzer light '''
        if light > 0 and light < 5:
            self.buffer[light+1] = 0x00
        self.send_buffer()


    def get_pressed(self) -> list:
        ''' Get a list of currently pressed buzzers '''
        pressed = []
        if self.data[3] == 33:
            pressed += [1, 2]
        elif self.data[3] == 1:
            pressed.append(1)
        elif self.data[3] == 32:
            pressed.append(2)
        if self.data[4] == 132:
            pressed += [3, 4]
        elif self.data[4] == 4:
            pressed.append(3)
        elif self.data[4] == 128:
            pressed.append(4)
        self.data_changed = False
        return pressed


    def close(self) -> None:
        ''' Close the connection to the device '''
        self.device.close()
