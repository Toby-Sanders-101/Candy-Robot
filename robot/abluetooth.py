import aioble
from aioble import device
import bluetooth
import machine
import asyncio
import uasyncio
import random
from motor_controller import *

def uid():
    """ Return the unique id of the device as a string """
    return "{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}".format(
        *machine.unique_id())

print("uid =",uid())

led = machine.Pin("LED", machine.Pin.OUT)
led.off()
#class Service:
#    def __init__(self, uuid):
#        self.uuid = uuid
#        self.characteristics = []

#class Characteristic(BaseCharacteristic):
#    def __init__(
#        self,
#        service,
#        uuid,
#        read=False,
#        write=False,
#        write_no_response=False,
#        notify=False,
#        indicate=False,
#        initial=None,
#        capture=False,
#   ):

#async def advertise(
#    interval_us,
#    adv_data=None,
#    resp_data=None,
#    connectable=True,
#    limited_disc=False,
#    br_edr=False,
#    name=None,
#    services=None,
#    appearance=0,
#    manufacturer=None,
#    timeout_ms=None,
#):

# appearances:
# remote control = 0x0180 - 0x01BF
# motorised vehicle = 0x08C0 - 0x08FF

# services:
# device information = 0x180A
# PhysicalActivityMonitorService = 0x183E
# media control = 0x1848
# GAP = 0x1800

# characteristics:
# electric current = 0x2AEE
# voltage = 0x2B18

# device name = 0x2A00
# appearance = 0x2A01
# battery level = 0x2A19
# serial number = 0x2A25 = uid()
# manufacturer name = 0x2A29

device_name = "Candy Robot"
robot_service_uuid = bluetooth.UUID(0x183E)
general_char_uuid = bluetooth.UUID(0x2AEE)

class ble_robot:
    def __init__(self):
        self.connection = None
        self.connected = False
        
        self.device = aioble.Device(aioble.ADDR_RANDOM, uid())
        
        self.appearance = 0x08C0
        
        self.device_service_uuid = bluetooth.UUID(0x180A)
        self.device_service = aioble.Service(self.device_service_uuid)
        aioble.Characteristic(self.device_service, bluetooth.UUID(0x2A00), read=True, initial=bytearray(b"Candy Robot"))
        #aioble.Characteristic(self.device_service, bluetooth.UUID(0x2A01), read=True, initial=bytearray(str(self.appearance).encode("utf-8")))
        self.battery_char = aioble.Characteristic(self.device_service, bluetooth.UUID(0x2A19), read=True, initial=bytearray(str(100).encode("utf-8")))
        #aioble.Characteristic(self.device_service, bluetooth.UUID(0x2A25), read=True, initial=bytearray(uid().encode("utf-8")))
        #aioble.Characteristic(self.device_service, bluetooth.UUID(0x2A29), read=True, initial=bytearray(b"Digital Academy"))
        
        self.robot_service = aioble.Service(robot_service_uuid)
        self.general_char = aioble.Characteristic(self.robot_service, general_char_uuid, write=True, read=True, capture=True)
        
        aioble.register_services(self.device_service, self.robot_service)
        
        def func(connection):
            battery_level = random.randint(0, 100)
            print("battery level:", battery_level)
            self.battery_char.write(bytearray(str(-battery_level).encode("utf-8")))
            return bytearray(battery_level)
        
        self.battery_char.on_read = func

        self.robot_machine = robot_machine()
    
    async def advertise_task(self):
        while True:
            await asyncio.sleep(1)
            if not self.connected:
                try:
                    self.connection = await aioble.advertise(1_000, name=device_name, 
                        services=[self.device_service_uuid, robot_service_uuid], appearance=self.appearance) # type: ignore
                    if self.connection:
                        self.connected = True
                        print("connected")
                        led.on()
                except Exception as e:
                    print("advertise error:", e)
                    self.connected = False
                    led.off()
                    self.connection = None
            else:
                temp_bool = self.connection.is_connected() # type: ignore
                try:
                    if not temp_bool: # type: ignore
                        self.connected = False
                        print("disconnected")
                        led.off()
                        self.connection = None
                except Exception as e:
                    print("is_connected error:", e)

    async def robot_task(self):
        while True:
            if self.connected:
                _, data = await self.general_char.written() # type: ignore
                data = data.decode("utf-8")
                print(data)
                data_arr = data.split(" ")
                x, y, open = float(data_arr[0]), float(data_arr[1]), int(data_arr[2])
                if open == 1:
                    self.robot_machine.open()
                elif open == 0:
                    self.robot_machine.close()
                self.robot_machine.move(x, y)
                await uasyncio.sleep_ms(100)
            else:
                await asyncio.sleep(1)
    
    async def blink_task(self):
        while True:
            if self.connected:
                await asyncio.sleep(0.5)
            else:
                self.robot_machine.move(0,0)
                await asyncio.sleep(0.1)
            led.toggle()
    
    async def start(self):
        try:
            tasks = [
                asyncio.create_task(self.advertise_task()),
                asyncio.create_task(self.robot_task()),
                asyncio.create_task(self.blink_task())
            ]
            await asyncio.gather(*tasks)
        except Exception as e:
            print("start error:", e)

asyncio.run(ble_robot().start())