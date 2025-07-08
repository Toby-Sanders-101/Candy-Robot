# Candy-Robot



## Overview

This is a remote control machine that stores and dispenses sweets. It was a project taken on by myself (Toby Sanders), Dakota Parsons, and Brad Man as part of Digital Academy at Callywith College in the academic year 2024/25.

It uses two Raspberry Pi Picos (Wireless, version 2) - one inside the remote, one inside the 'robot'. They communicate via bluetooth.

The remote uses a joystick to take movement inputs from the users, and they can press down on the joystick too to release the sweets. 

The robot uses four motors to move around and two other motors to release the sweets - one to open a gate for the sweets to pass through, and the other motor moves the sweets around in the bowl to ensure they don't clog up.



## Software

All the (most up-to-date) code for the Picos has been uploaded to this repo. It uses micropython and the aioble (asychronous bluetooth) module to do most the work. Most of the code is easy to understand and I've included some of the details for the bluetooth in the python files.

The robot advertises itself as a bluetooth device with two services:
* The device information service (uuid=0x180A), which has two characteristics:
  - The device name characteristic (uuid=0x2A00) = "Candy Robot"
  - The battery level characteristic (uuid=0x2A19) which is currently not used
* The service for the data for the motors (uuid=0x183E), which has one characteristsic:
  - The characteristic that handles the data for the motors (uuid=0x2AEE)

The remote scans for this device and once found, it will routinely write the state of the joystick to the robot. The Pico in the remote uses the analogue to digital converter (ADC) pins 26, 27 and 28 to get the state of the joystick as two values between 0-65535 for the x and y axis, and a integer 0 or 1 for whether the joystick is being pressed or not (select axis). This raw data is converted to integers where the x and y axis are each expressed as a number between -4 and 4 inclusive, and the select axis is transformed to ensure that 0 corresponds to the joystick not being pressed and 1 corresponds to the joystick being pressed.

The Pico in the robot will routinely read the data that is sent by the other Pico. It reads this data as three integers which can be parsed and converted into Pulse Width Modulation duties to control the speed of the motors
