from serial import Serial
from serial import EIGHTBITS
from serial import PARITY_NONE
from serial import STOPBITS_ONE

def Setup_serial(port='COM5'):
    while True:
        try:
            '''
            ser = Serial(
            port = port,
            baudrate = 9600,
            bytesize = EIGHTBITS,
            parity = PARITY_NONE,
            stopbits = STOPBITS_ONE,
            timeout = 1,
            xonxoff = False,
            rtscts = False,
            dsrdtr = False,
            writeTimeout = 2
            )
            '''
            ser = Serial(port = port, baudrate = 9600, timeout = 1)
            if(ser.isOpen() == False):
                ser.open()
            else:
                return ser
        except FileNotFoundError as e:
            print("You're either not connected or the port", port, "is wrong")
        except Exception as e:
            print("Error connecting to serial with error e=", e)
