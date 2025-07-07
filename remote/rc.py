import machine
import time
import math

def transform(num): # 0 to 2^16-1
    num -= 2**15 # -2^15 to 2^15-1
    return int(round(num/(2**13))) # -2^2 to 2^2
    

class remote_machine:
    def __init__(self):
        self.piny = machine.ADC(26)
        self.pinx = machine.ADC(27)
        self.sel = machine.Pin(28, machine.Pin.IN, machine.Pin.PULL_UP)
    
    def read_all(self):
        return (transform(self.pinx.read_u16()), transform(self.piny.read_u16()), (1-self.sel.value()))

def test():
    remote = remote_machine()
    while True:
        a,b,c = remote.read_all()
        #print(str(a) +"\t"+ str(b) +"\t"+ str(c))
        time.sleep(0.1)

if __name__ == "__main__":
    test()