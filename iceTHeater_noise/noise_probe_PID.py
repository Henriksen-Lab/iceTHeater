# Written by Shilling Du 7/11/2022
import sys, os, time, threading, tkinter
import numpy as np
from decimal import Decimal
import matplotlib.pyplot as plt

folder_path = os.getcwd()
if folder_path not in sys.path:
    sys.path.append(folder_path)  # easier to open driver files as long as Simple_DAQ.py is in the same folder with drivers
from keithley_2400 import get_ohm_4pt_2000
from Arduino_control import arduino_write
from Cernox import get_T_cernox_2


'''-------------------------------------------------------Main------------------------------------------------------'''
keithley2000_gpib = 'GPIB0::18::INSTR'
Arduino = 'COM9'

update_flag = True
class Mypid:
    def __init__(self):
        self.kp = 1.0
        self.ki = 0.1
        self.kd = 0.05
        self.sample_time = 5
        self.LastErr = 0
        self.errsum = 0
        self.limit = (0,100)
        self.setpoint = 0

    def read(self):
        self.reading = get_T_cernox_2(get_ohm_4pt_2000(keithley2000_gpib))
        print("Temp now is ", self.reading)

    def write(self):
        arduino_write(self.output, Arduino)
        print("Arduino set to ", self.output)

    def pid_start(self):
        print("PID initializing")
        self.read()
        error = float(self.setpoint - self.reading)
        self.lastErr = error
        time_interval = self.sample_time
        self.errsum += error * time_interval
        derr = (error - self.lastErr) / time_interval
        self.output = self.kp * error + self.ki * self.errsum + self.kd * derr
        self.output = max(min(self.output, self.limit[1]), self.limit[0])
        self.lastErr = error
        self.lasttime = time.time()
        self.write()
        print("PID initialized")

    def pid_update(self):
        print("PID updating")
        self.read()
        error = float(self.setpoint - self.reading)
        time_interval = time.time()-self.lasttime
        self.errsum += error * time_interval
        derr = (error - self.lastErr) / time_interval
        self.output = self.kp * error + self.ki * self.errsum + self.kd * derr
        self.output = max(min(self.output, self.limit[1]), self.limit[0])
        self.lastErr = error
        self.lasttime = time.time()
        self.write()
        print("PID updated")

    def manual_tune(self,newkp,newki,newkd):
        self.kp = newkp
        self.ki = newki
        self.kd = newkd

    def pid_run(self):
        self.pid_start()
        fg = plt.figure()
        plt.xlabel("time(s)")
        plt.ylabel("Temp(K)")
        t_now = time.time()
        while update_flag:
            self.pid_update()
            plt.plot(self.lasttime - t_now, self.reading, '.r')
            plt.xlim([0, self.lasttime - t_now + 1])
            plt.pause(0.5)
            print(time.asctime(time.localtime(time.time())), "\nTemp =", self.reading, "K", ", Set point =", self.setpoint, "K")



    def auto_tune(self):
        #Ziegler–Nichols Method
        self.ki = 0
        self.kd = 0
        oal = False
        for i in range(0,10000):
            if oal:
                break
            self.kp = i/100
            self.pid_start()
            self.readinglog = []
            self.timelog = []
            for j in range(0,1000):
                self.pid_update()
                self.readinglog += [self.reading]
                self.timelog += [self.lasttime]

                if self.reading> 1.5* self.setpoint:
                    oal = True
            plot_save(self.readinglog, self.timelog,self.kp)
        print("overload")


def plot_save(x,y,kp):
    fg = plt.figure()
    plt.plot(x-x[0], y)
    plt.xlabel('time(s)')
    plt.ylabel('Temp(K)')
    plt.title(f"PIO_at_kp={kp}")
    fg.savefig(r"C:\Users\ICET\Documents\GitHub\iceTHeater\graph" + f'\PIO_at_kp={kp}.jpg', bbox_inches='tight', dpi=150)
    plt.close()
    time.sleep(0.1)

def pop_window():
    window = tkinter.Tk()
    window.title('Set temp')
    window.geometry('300x200')
    tkinter.Label(window,text ='Input set temperature', height=2).pack()
    entry = tkinter.Entry(window)
    entry.pack()
    t1()
    def on_click():
        global update_flag
        value = entry.get()
        pid.setpoint = Decimal(float(value)).quantize(Decimal("0.00"))
        print("Set point = " + str(pid.setpoint) + "K")
        update_flag = True
        time.sleep(1)
        #window.destroy()

    tkinter.Button(window, text="Input", command = on_click).pack()
    def exit():
        global update_flag
        update_flag = False
        time.sleep(1)
        sys.exit()
    tkinter.Label(window,text ="Plese press here to Exit", height=2).pack()
    tkinter.Button(window, text="Exit", command = exit).pack()
    window.mainloop()

def t1():
    t1 = threading.Thread(target = pid.pid_run)
    t1.start()

pid = Mypid()
pop_window()
