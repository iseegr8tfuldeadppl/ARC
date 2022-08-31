import traceback
from nrf24 import *
import time

reading_address = "readp" # 1SRVR
writing_address = "writp" # 1CLNT

nrf = None
mode = None
def sendNRFFinishMsg(pi):
    global nrf
    global mode
    # bytearray([0x54, 0x43]).decode()

    # Create NRF24 object.
    # PLEASE NOTE: PA level is set to MIN, because test sender/receivers are often close to each other, and then MIN works better.
    if nrf == None:
        nrf = NRF24(pi, ce=25, payload_size=RF24_PAYLOAD.DYNAMIC, channel=0x76, data_rate=RF24_DATA_RATE.RATE_250KBPS, pa_level=RF24_PA.MIN)
        nrf.set_address_bytes(len(reading_address))
        nrf.set_retransmission(15, 15)
        nrf.open_writing_pipe(writing_address)
        nrf.open_reading_pipe(RF24_RX_ADDR.P0, reading_address)

    # Display the content of NRF24L01 device registers.
    #nrf.show_registers()
 
    # Enter a loop receiving data on the address specified.
    print("mode", mode)
    while mode == "NRF":
        try:
            nrf.reset_packages_lost()
            nrf.send(bytes("Finish", encoding='utf-8'))

            while nrf.is_sending():
                time.sleep(0.0004)

            if nrf.get_packages_lost() == 0:
                print(f'Success: lost={nrf.get_packages_lost()}, retries={nrf.get_retries()}')
                # read ack
                time.sleep(0.1)
                if nrf.data_ready():
                    pipe = nrf.data_pipe()
                    payload = nrf.get_payload()
                    print(payload.decode())
                    return
            else:
                print(f'Error: lost={nrf.get_packages_lost()}, retries={nrf.get_retries()}')

            # Sleep 1 ms.
            time.sleep(0.01) # 0.001
        except Exception as e:
            print("ol")
            traceback.print_exc()
            #nrf.power_down()