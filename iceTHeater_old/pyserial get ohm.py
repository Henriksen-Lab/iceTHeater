#Written by Shilling Du 11/1/2020
import serial, sys, time, cmath, threading, tkinter
import numpy as np
from decimal import Decimal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from multiprocessing import Process


	
def get_T(R):
	c1=[5.5582108,-6.41962,2.86239,-1.059453,0.328973,0.081621997,0.012647,0.00088100001,-0.001982,0.00099099998]
	c14=[43.140221,-38.004025,8.0877571,-0.913351,0.091504,-0.0036599999,-0.0060470002]
	c80=[177.56671,-126.69688,22.017452,-3.116698,0.59847897,-0.111213,0.01663,-0.0067889998]

	if R > 665.0:
		ww1 = c1
		for i in range(0,len(c1)):
			ww1[i] = c1[i]*cmath.cos(i*cmath.acos(((cmath.log10(R)-2.77795312391)-(4.06801081354-cmath.log10(R)))/(4.06801081354-2.77795312391)))
		result = sum(ww1)
	elif R > 184.8:
		ww14 = c14
		for i in range(0,len(c14)):
			ww14[i] = c14[i]* cmath.cos(i* cmath.acos(((cmath.log10(R)-2.22476915988)-(2.86208992852-cmath.log10(R)))/(2.86208992852-2.22476915988)))
		result = sum(ww14)
	else:
		ww80 = c80
		for i in range(0,len(c80)):
			ww80[i]= c80[i]*cmath.cos(i*cmath.acos(((cmath.log10(R)-1.72528854694)-(2.3131455111-cmath.log10(R)))/(2.3131455111-1.72528854694)))
		result = sum(ww80)
	return Decimal(result.real).quantize(Decimal("0.00"))

def open_equi_initial():
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

def open_equi_read():
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
	
def open_arduino_write(t):
	global arduino_name
	arduino = serial.Serial(ardunio_name,9600,timeout=0) 
	flag = arduino.is_open
	#print(t)
	if 100<=t<1000:
		tt = "CG "+ str(t) + "E"
	elif 10<=t<100:
		tt = "CG 0"+ str(t) + "E"
	elif t<10:
		tt = "CG 00"+ str(t) + "E"
	else:
		print("Temp out of range")
	arduino.write(bytes(tt,'utf-8'))
	time.sleep(0.5)
	'''for x in(bytes(tt,'utf-8')):
		print (x)'''
	arduino.close()
	
def initial_arduino():
	global arduino_name
	arduino = serial.Serial(ardunio_name,9600,timeout=0)
	flag = arduino.is_open
	tt = "CG 000E"
	ttt = "CS 000E"
	arduino.write(bytes(tt,'utf-8'))
	time.sleep(0.1)
	arduino.write(bytes(ttt,'utf-8'))
	time.sleep(0.1)
	arduino.close()

def open_arduino_set(t):
	global arduino_name
	arduino = serial.Serial(ardunio_name,9600,timeout=0)
	flag = arduino.is_open
	#print(t)
	if 10<=t<100:
		tt = "CS 0"+ str(t) + "E"
	elif t<10:
		tt = "CS 00"+ str(t) + "E"
	else:
		tt = "CS "+ str(t) + "E"
	arduino.write(bytes(tt,'utf-8'))
	'''for x in(bytes(tt,'utf-8')):
			print (x)'''
	time.sleep(0.5)
	arduino.close()
	
def read_arduino(arduino):
	while 1:
		out = arduino.read(100).decode('ISO-8859-1')
		#print(out) # Test Arduino connection
		time.sleep(1.3)
		
def update():
	global set_temp, t_now, update_flag
	while 1:
		if update_flag:
			open_equi_initial()
			initial_arduino()
			plt.ion()
			plt.figure(1)
			plt.xlabel("time(s)")
			#plt.ylim([0,310])
			plt.ylabel("Temp(K)")
			t_now = time.time()
			pretemp =0
			while 1:
				temp = open_equi_read()
				open_arduino_set(set_temp)
				if abs(temp-pretemp)<100 or pretemp ==0:
					open_arduino_write(temp)
					plt.plot(time.time()-t_now,temp,'.r')
					plt.xlim([0,time.time()-t_now+1])
					plt.pause(0.5)
					print(time.asctime(time.localtime(time.time())),"\nTemp =",temp,"K", ", Set point =", set_temp,"K")
					pretemp = temp
				else:
					print(time.asctime(time.localtime(time.time())),"\nError when read")
			plt.close()
		else:
			time.sleep(1)
			print("Arduino disconeected")
			
def pop_window():
	window = tkinter.Tk()
	window.title('Set temp')
	window.geometry('300x200')
	tkinter.Label(window,text ='Input set temperature', height=2).pack()
	entry = tkinter.Entry(window)
	entry.pack()
	def on_click():
		global set_temp, update_flag
		value = entry.get()
		set_temp = Decimal(float(value)).quantize(Decimal("0.00"))
		plt.title("Set point = " + str(set_temp) + "K")
		update_flag = True
		time.sleep(1)
		window.destroy()
	tkinter.Button(window, text="Input", command = on_click).pack()
	def exit():
		global update_flag
		update_flag = False
		initial_arduino()
		time.sleep(1)
		thread2.exit()		
	tkinter.Label(window,text ="Plese press here to Exit", height=2).pack()
	tkinter.Button(window, text="Exit", command = exit).pack()
	window.mainloop()
	
ardunio_name = '/dev/tty.usbmodem14301'
arduino = serial.Serial(ardunio_name,9600,timeout=0)
thread = threading.Thread(target=read_arduino, args=(arduino,))
thread.start()
time.sleep(0.1)
set_temp = 0
update_flag = False
stop_thread = False
process2 = Process(target=pop_window())
process2.start()
process1 = Process(target=update())
process1.start()
process1.join()
process2.join()





