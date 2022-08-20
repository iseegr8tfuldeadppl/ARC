from serial_tools.setup_serial import *
from serial_tools.clean import *
from serial_tools.read import *
import keyboard
import cv2

def send_command(serial, command):
    was_connecting = False
    port = "COM4"
    while True:

        if serial==None or not serial.isOpen():
            serial = Setup_serial(port)
            was_connecting = True
            print("Connecting..")
        else:
            if was_connecting:
                was_connecting = False
                print("Connected")

            
            cv2.waitKey(1)
            if keyboard.is_pressed('q') == True or keyboard.is_pressed('esc') == True or 0xFF == ord('q'):
                return None

            # send the command
            serial.write(bytes(command + '\n', 'utf-8')) # + '\n'

            # then wait for an Ok
            _, bundle = Read(serial, False, port)
            message = Clean(bundle)

            print("message", message)

            if not message:
                continue

            print("Arduino printed:", message)

            if message.startswith("Ok"):
                print("Ok")
                break

            


    return serial
