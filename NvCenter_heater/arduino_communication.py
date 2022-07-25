# Written by Shilling Du 7/25/2022
import serial, time
from decimal import Decimal

def arduino_set(arduino_name, t):
    arduino = serial.Serial(arduino_name, 9600, timeout=0)
    flag = arduino.is_open
    # print(t)
    t = Decimal(float(t)).quantize(Decimal("0.0"))
    if 10 <= t < 100:
        tt = "CS 0" + str(t) + "E"
    elif t < 10:
        tt = "CS 00" + str(t) + "E"
    else:
        tt = "CS " + str(t) + "E"
    arduino.write(bytes(tt, 'utf-8'))
    time.sleep(0.5)
    arduino.close()



def arduino_read_set(arduino_name):
    arduino = serial.Serial(arduino_name, 9600, timeout=5)
    startMarker = '('
    endMarker = ')'
    receivedChars = []
    newdata = False
    recvInProgress = False
    while newdata == False:
        out = arduino.read(1).decode('utf-8')
        if out == startMarker and recvInProgress == False:
            recvInProgress = True
        elif out != endMarker and recvInProgress == True:
            receivedChars += [out]
        elif out == endMarker and recvInProgress == True:
            recvInProgress = False
            newdata = True
    output = ''.join(receivedChars)
    output = float(output)
    arduino.close()
    return output

def arduino_read(arduino_name):
    arduino = serial.Serial(arduino_name, 9600, timeout=5)
    startMarker = '<'
    endMarker = '>'
    receivedChars = []
    newdata = False
    recvInProgress = False
    while newdata == False:
        out = arduino.read(1).decode('utf-8')
        if out == startMarker and recvInProgress == False:
            recvInProgress = True
        elif out != endMarker and recvInProgress == True:
            receivedChars += [out]
        elif out == endMarker and recvInProgress == True:
            recvInProgress = False
            newdata = True
    output = ''.join(receivedChars)
    output = float(output)
    arduino.close()
    return output

def arduino_read_output(arduino_name):
    arduino = serial.Serial(arduino_name, 9600, timeout=5)
    startMarker = '{'
    endMarker = '}'
    receivedChars = []
    newdata = False
    recvInProgress = False
    while newdata == False:
        out = arduino.read(1).decode('utf-8')
        if out == startMarker and recvInProgress == False:
            recvInProgress = True
        elif out != endMarker and recvInProgress == True:
            receivedChars += [out]
        elif out == endMarker and recvInProgress == True:
            recvInProgress = False
            newdata = True
    output = ''.join(receivedChars)
    output = float(output)
    arduino.close()
    return output