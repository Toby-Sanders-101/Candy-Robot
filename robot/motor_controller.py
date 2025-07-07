from machine import Pin, PWM


class robot_machine:
    def __init__(self):
        self.hatch_open = Pin(0, Pin.OUT)
        self.hatch_close = Pin(1, Pin.OUT)
        self.hatch_open.off()
        self.hatch_close.off()

        self.left_motor_driver_forward = PWM(Pin(14, Pin.OUT))
        self.left_motor_driver_backward = PWM(Pin(15, Pin.OUT))
        self.right_motor_driver_forward = PWM(Pin(16, Pin.OUT))
        self.right_motor_driver_backward = PWM(Pin(17, Pin.OUT))

        self.left_motor_driver_forward.freq(1000)
        self.left_motor_driver_backward.freq(1000)
        self.right_motor_driver_forward.freq(1000)
        self.right_motor_driver_backward.freq(1000)

    def open(self):
        self.hatch_open.off()
        self.hatch_close.off()

    def close(self):
        self.hatch_open.on()
        self.hatch_close.on()
    
    def move(self, x, y): # -1 < x,y < 1. +y = forwards
        # left motor speed = y+x
        # right motor speed = y-x

        x,y = x,y
        multiplier = 2^13
        self.left_motor_driver_forward.duty_u16(int(multiplier*(y+x)))
        self.left_motor_driver_backward.duty_u16(int(-multiplier*(y+x)))
        self.right_motor_driver_forward.duty_u16(int(multiplier*(y-x)))
        self.right_motor_driver_backward.duty_u16(int(-multiplier*(y-x)))

#robot_machine().forward()


def test():
    robot = robot_machine()
    while True:
        x, y = input("move x)"), input("move y)")
        robot.move(x,y)

#pin0 = Pin(0, Pin.OUT)
#pin1 = Pin(1, Pin.OUT)
#pin2 = Pin(2, Pin.OUT)
#pin3 = Pin(3, Pin.OUT)#

#if False:
#    pin0.on()
#    pin1.off()
#    pin2.on()
#    pin3.off()
#else:
#    pin0.off()
#    pin1.on()#
#    pin2.off()
#    pin3.on()