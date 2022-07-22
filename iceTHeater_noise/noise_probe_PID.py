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
        self.sample_time = 3
        self.LastErr = 0
        self.errsum = 0
        self.limit = (0,100)
        self.setpoint = 0
        self.readinglog = []
        self.timelog = []

    def read(self):
        self.reading = float(get_T_cernox_2(get_ohm_4pt_2000(keithley2000_gpib)))
        print("Temp now is ", self.reading)

    def write(self):
        arduino_write(self.output, Arduino)
        print("Arduino set to ", self.output)

    def close(self):
        self.output = 0
        self.write()

    def pid_start(self):
        print("PID initializing")
        self.read()
        error = float(self.setpoint) - float(self.reading)
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
        time.sleep(self.sample_time)

    def pid_update(self):
        print("PID updating")
        self.read()
        error = float(self.setpoint) - float(self.reading)
        time_interval = time.time()-self.lasttime
        if abs(self.reading-self.setpoint)>0.5 and self.output==100:
            self.errsum=0
        else:
            self.errsum += error * time_interval
        derr = (error - self.lastErr) / time_interval
        self.output = self.kp * error + self.ki * self.errsum + self.kd * derr
        self.output = max(min(self.output, self.limit[1]), self.limit[0])
        self.lastErr = error
        self.lasttime = time.time()
        self.write()
        print("PID updated")
        time.sleep(self.sample_time)

    def manual_tune(self,newkp,newki,newkd):
        self.kp = newkp
        self.ki = newki
        self.kd = newkd

    def pid_run(self):
        self.pid_reset()
        self.pid_start()
        fg = plt.figure()
        self.fg = fg
        plt.xlabel("time(s)")
        plt.ylabel("Temp(K)")
        t_now = time.time()
        while update_flag:
            print(time.asctime(time.localtime(time.time())), "\nTemp =", self.reading, "K", ", Set point =",
                  self.setpoint, "K")
            self.pid_update()
            plt.title(f"PIO_at_kp={pid.kp}, ki={pid.ki},kd={pid.kd}, setpoint = {pid.setpoint}")
            plt.plot(self.lasttime - t_now, self.reading, '.r')
            self.readinglog += [self.reading]
            self.timelog += [self.lasttime - t_now]
            plt.xlim([0, self.lasttime - t_now + 1])
            plt.pause(0.5)


    def pid_reset(self):
        self.LastErr = 0
        self.errsum = 0

    def auto_tune(self):
        #Ziegler–Nichols Method
        self.ki = 0
        self.kd = 0
        oal = False
        for i in range(0,5):
            if oal:
                break
            self.kp = i*100+600
            self.pid_start()
            self.readinglog = []
            self.timelog = []
            for j in range(0,500):
                self.pid_update()
                self.readinglog += [self.reading]
                self.timelog += [self.lasttime]
                print("plotted ",j,", at kp = ", self.kp)

                if float(self.reading)> 1.5* float(self.setpoint):
                    self.close()
                    oal = True
                    break
            plot_save(self.timelog, self.readinglog)
        print("overload")


def plot_save(x,y,order):
    fg1 = plt.figure()
    plt.plot([a-x[0] for a in x], y)
    plt.xlabel('time(s)')
    plt.ylabel('Temp(K)')
    plt.title(f"PIO_at_kp={pid.kp}, ki={pid.ki},kd={pid.kd}, setpoint = {pid.setpoint}")
    fg1.savefig(r"C:\Users\ICET\Documents\GitHub\iceTHeater\graph" + f'\PIO_at_setpoint={int(pid.setpoint)}_{order}.jpg', bbox_inches='tight', dpi=150)
    plt.close()
    print("graph saved")
    np.savetxt(r"C:\Users\ICET\Documents\GitHub\iceTHeater\graph" + f'\PIO_at_setpoint={int(pid.setpoint)}.{order}', np.column_stack(([a-x[0] for a in x], y)), delimiter='\t',
               header=f"PIO_at_kp={pid.kp}, ki={pid.ki},kd={pid.kd}, setpoint = {pid.setpoint}\n"+f"time(s)_{pid.kp}\t\t\tTemp(K)_{pid.kp}\t\t\t")
    print("data saved")
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

'''--------------------------Main------------------------------------------------'''
pid = Mypid()
pid.manual_tune(newkp=337,newki=0.69,newkd=0) #Optimized value
'''normal run, set 1 temp'''
#pop_window()

'''just reading temp'''
#while 1:
#   pid.read()

'''sweep temp from temp now to the 80K at rate = 1K/10min'''
target_value_temp = 80
delaytime =300
step_size = 1
num_steps = int(np.floor(abs(target_value_temp) / (step_size))) + 1
pid.read()
t1()
k=0
for val in np.linspace(float(pid.reading), target_value_temp, num_steps):
    pid.setpoint = val
    print("\nnew setpoint at ", val)
    time.sleep(delaytime)
    plot_save(pid.timelog, pid.readinglog, k)
    pid.readinglog = []
    pid.timelog = []
    k += 1
pid.close()
sys.exit()