import aioble
from aioble import device
import bluetooth
import machine
import asyncio
import uasyncio
import random
import rc

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

class ble_remote:
    def __init__(self):
        self.reset()
        self.remote = rc.remote_machine()
    
    def reset(self):
        self.connection = None
        self.connected = False
        self.service = None
        self.characteristic = None
    
    async def search_task(self):
        while True:
            if not self.connected:
                try:
                    async with aioble.scan(10_000, interval_us=30_000, window_us=30_000, active=True) as scanner: # type: ignore
                        async for scan_result in scanner:
                            print(scan_result, scan_result.name())
                            if scan_result.name() == device_name:
                                print("attempting to connect to", scan_result.name())
                                try:
                                    self.connection = await scan_result.device.connect(10_000) # type: ignore
                                    if self.connection:
                                        self.connected = True
                                        print(f"connected to {scan_result.name()}")
                                        await scanner.cancel() # type: ignore
                                        
                                        self.service = await self.connection.service(robot_service_uuid) # type: ignore
                                        self.characteristic = await self.service.characteristic(general_char_uuid) # type: ignore
                                        
                                        break
                                    else:
                                        self.reset()
                                        print(f"attempt to connect to {scan_result.name()} failed")
                                except Exception as e:
                                    self.reset()
                                    print("connect error:", e)
                        else:
                            print("device not found")
                            await scanner.cancel() # type: ignore
                            print("new loop\n")
                except Exception as e:
                    print("scan error:", e)
                    print("new loop\n")
                await asyncio.sleep(5)
            else:
                await asyncio.sleep(10)
    
    async def remote_task(self):
        while True:
            await uasyncio.sleep_ms(10)
            if self.connected:
                if self.connection.is_connected(): # type: ignore
                    if self.characteristic:
                        try:
                            data = await self.characteristic.read() # type: ignore
                            print(data)
                            x,y,sel = self.remote.read_all()
                            await self.characteristic.write(bytearray((str(x)+" "+str(y)+" "+str(sel)).encode("utf-8"))) # type: ignore
                        except Exception as e:
                            print("read or write error:", e)
                else:
                    self.reset()
                    print("disconnected")
    
    async def blink_task(self):
        while True:
            if self.connected:
                await asyncio.sleep(0.4)
            await asyncio.sleep(0.1)
            led.toggle()
    
    async def start(self):
        try:
            tasks = [
                #asyncio.create_task(find_remote()),
                asyncio.create_task(self.search_task()),
                asyncio.create_task(self.remote_task()),
                asyncio.create_task(self.blink_task())
            ]
            await asyncio.gather(*tasks)
        except Exception as e:
            print("start error:", e)
        finally:
            led.off()
        
asyncio.run(ble_remote().start())