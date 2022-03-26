def Read(ser, rip, port):
    if ser==None or ser.isOpen() == False:
        ser = Setup_serial(port)
        print("fuck")
    else:
        try:
            b = ser.readline() # read a byte string
            rip = False
            return rip, b
        except:
            rip = True
            return rip, None
