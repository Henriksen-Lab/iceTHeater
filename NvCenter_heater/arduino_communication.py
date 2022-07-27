# Written by Shilling Du 7/25/2022
import serial, time
from decimal import Decimal

def arduino_set(arduino_name, t):
    try:
        arduino = serial.Serial(arduino_name, 9600, timeout=0)
        flag = arduino.is_open
        # print(t)
        t = Decimal(float(t)).quantize(Decimal("0.0"))
        tt = 'k' + str(t) + 't'
        arduino.write(bytes(tt, 'utf-8'))
        time.sleep(0.5)
    finally:
        arduino.close()

def arduino_set_pid(arduino_name, pid):
    try:
        arduino = serial.Serial(arduino_name, 9600, timeout=0)
        flag = arduino.is_open
        # print(t)
        arduino.write(bytes(pid, 'utf-8'))
        time.sleep(0.5)
    finally:
        arduino.close()

def arduino_read_set(arduino_name):
    try:
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
    finally:
        arduino.close()
    return output

def arduino_read(arduino_name):
    try:
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
    finally:
        arduino.close()
    return output

def arduino_read_output(arduino_name):
    try:
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
    finally:
        arduino.close()
    return output

def arduino_read_pid(arduino_name):
    try:
        arduino = serial.Serial(arduino_name, 9600, timeout=5)
        startMarker = '$'
        endMarker = '&'
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
    finally:
        arduino.close()
    return output