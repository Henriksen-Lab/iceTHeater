import serial,time

def arduino_write(power,address):
    arduino = serial.Serial(port=address, baudrate=9600, timeout=2)
    flag = arduino.is_open
    time.sleep(2)  # allow time for serial port to open
    if 0<= power<= 100:
        byte = bytes('<'+str(power)+'>','utf-8')
    else:
        print("output set error, has to be int 0-100")
        byte = 0

    arduino.write(byte)
    arduino.flushOutput()
    time.sleep(0.05)
    arduino.close()


