#Written by Shilling Du 7/11/2022
import serial
def keithley_initial():
    keithley = serial.Serial('/dev/tty.usbserial-PX4TWTWW',9600,timeout=1)
    flag = keithley.is_open
    #keithley.write(b"*idn? \r\n")
    #keithley.write(b"status:measurement:enable 512; *sre 1 \r\n")
    keithley.write(b"*rst")
    keithley.write(b":SYST:BEEP:STAT OFF\r\n")
    keithley.write(b"*cls\r\n")
    keithley.write(b":SENS:FUNC 'VOLTage:DC'\r\n")
    keithley.write(b":SENS:VOLTage:DC:RANGE:Auto 1\r\n")
    time.sleep(1)
    keithley.close()

def keithlry_read():
    keithley = serial.Serial('/dev/tty.usbserial-PX4TWTWW',9600,timeout=1)
    keithley.write(b":MEAS:VOLTage:DC?\r\n")
    time.sleep(1.5)
    out = ''
    read = 0
    while keithley.inWaiting() > 0:
         out += keithley.read().decode("ascii")
    if out != '':
        read = float(out)* (10**6)/(0.8765)
    #print ("Resistance is ", read, "Ohm")
    #print ("Temp is ", get_T(read),"K")
    keithley.close()
    return get_T(read)