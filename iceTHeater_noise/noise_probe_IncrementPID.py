# Written by Shilling Du 7/11/2022
import sys, os, time, threading, tkinter
import numpy as np
from decimal import Decimal
import matplotlib.pyplot as plt

folder_path = os.getcwd()
if folder_path not in sys.path:
    sys.path.append(
        folder_path)  # easier to open driver files as long as Simple_DAQ.py is in the same folder with drivers
from keithley_2400 import get_ohm_4pt_2000
from Arduino_control import arduino_write
from Cernox import get_T_cernox_2
from hp34461A import get_voltage_hp34461a
from datetime import datetime

'''-------------------------------------------------------Main------------------------------------------------------'''
keithley2000_gpib = 'GPIB0::18::INSTR'
# keithley2400_gpib = 'GPIB0::25::INSTR'
Arduino = 'COM9'
hp34461a = 'GPIB0::17::INSTR'
data_dir = r"C:\Users\ICET\Desktop\Data\lyw"
my_note = "2022.07.18 Icet bn-g capcitively coupled device test"

update_flag = True


class Mypid:

    def __init__(self):
        self.kp = 1.0
        self.ki = 0.1
        self.kd = 0.05
        self.sample_time = 3
        self.lastErr = 0
        self.lastErr_2 = 0
        self.limit = (0, 100)
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
        derr = (error - self.lastErr) / time_interval
        # self.output = self.kp * error + self.ki * error* time_interval + self.kd * derr
        # self.output = max(min(self.output, self.limit[1]), self.limit[0])
        self.output = 0
        self.lastErr_2 = error
        self.lastErr = error
        self.lasttime = time.time()
        self.write()
        print("PID initialized")
        time.sleep(self.sample_time)

    def pid_update(self):
        print("PID updating")
        self.read()
        error = float(self.setpoint) - float(self.reading)
        time_interval = time.time() - self.lasttime
        # if abs(self.reading-self.setpoint)>0.5 and self.output==100:
        #   self.errsum=0
        # else:
        #    self.errsum += error * time_interval
        # derr = (error - self.lastErr) / time_interval
        self.output += self.kp * (error - self.lastErr) + self.ki * error * time_interval + self.kd * (
                    error - 2 * self.lastErr + self.lastErr_2) / time_interval
        self.output = max(min(self.output, self.limit[1]), self.limit[0])
        self.lastErr_2 = self.lastErr
        self.lastErr = error
        self.lasttime = time.time()
        self.write()
        print("PID updated")
        time.sleep(self.sample_time)

    def manual_tune(self, newkp, newki, newkd):
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
        # Ziegler–Nichols Method
        self.ki = 0
        self.kd = 0
        oal = False
        for i in range(0, 5):
            if oal:
                break
            self.kp = i * 100 + 600
            self.pid_start()
            self.readinglog = []
            self.timelog = []
            for j in range(0, 500):
                self.pid_update()
                self.readinglog += [self.reading]
                self.timelog += [self.lasttime]
                print("plotted ", j, ", at kp = ", self.kp)

                if float(self.reading) > 1.5 * float(self.setpoint):
                    self.close()
                    oal = True
                    break
            plot_save(self.timelog, self.readinglog)
        print("overload")


def plot_save(x, y, order):
    fg1 = plt.figure()
    plt.plot([a - x[0] for a in x], y)
    plt.xlabel('time(s)')
    plt.ylabel('Temp(K)')
    plt.title(f"PIO_at_kp={pid.kp}, ki={pid.ki},kd={pid.kd}, setpoint = {pid.setpoint}")
    fg1.savefig(
        r"C:\Users\ICET\Documents\GitHub\iceTHeater\graph" + f'\PIO_at_setpoint={int(pid.setpoint)}_{order}.jpg',
        bbox_inches='tight', dpi=150)
    plt.close()
    print("graph saved")
    np.savetxt(r"C:\Users\ICET\Documents\GitHub\iceTHeater\graph" + f'\PIO_at_setpoint={int(pid.setpoint)}.{order}',
               np.column_stack(([a - x[0] for a in x], y)), delimiter='\t',
               header=f"PIO_at_kp={pid.kp}, ki={pid.ki},kd={pid.kd}, setpoint = {pid.setpoint}\n" + f"time(s)_{pid.kp}\t\t\tTemp(K)_{pid.kp}\t\t\t")
    print("data saved")
    time.sleep(0.1)


def pop_window():
    window = tkinter.Tk()
    window.title('Set temp')
    window.geometry('300x200')
    tkinter.Label(window, text='Input set temperature', height=2).pack()
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
        # window.destroy()

    tkinter.Button(window, text="Input", command=on_click).pack()

    def exit():
        global update_flag
        update_flag = False
        time.sleep(1)
        sys.exit()

    tkinter.Label(window, text="Plese press here to Exit", height=2).pack()
    tkinter.Button(window, text="Exit", command=exit).pack()
    window.mainloop()


def t1():
    t1 = threading.Thread(target=pid.pid_run)
    t1.start()


'''--------------------------Main------------------------------------------------'''
pid = Mypid()
pid.manual_tune(newkp=0.3, newki=0.1, newkd=1)  # Optimized value
'''normal run, set 1 temp'''
# pop_window()

'''just reading temp'''
# while 1:
#   pid.read()

list = ['timestamp', 'temp', 'V_diode']


class Mydata:

    def __init__(self):
        self.timestamp = []
        self.temp = []
        self.V_diode = []
        # self.V_heater = []

    def update(self):
        self.timestamp += [time.time()]
        self.temp += [pid.reading]
        self.V_diode += [get_voltage_hp34461a(hp34461a)]
        # self.V_heater += [get_voltage_keithley(keithley2400_gpib)]

    def data_save(self, file_name='', order=1):
        axis = ''
        for x in list:
            axis += f"{x}_{order}\t\t\t"
        dataToSave = np.column_stack((self.timestamp, self.temp, self.V_diode))
        os.makedirs(data_dir + '\\' + datetime.now().strftime('%Y%m%d') + title, exist_ok=True)
        np.savetxt(data_dir + '\\' + datetime.now().strftime('%Y%m%d') + title + "/" + file_name, dataToSave,
                   delimiter='\t',
                   header=f"{datetime.now().strftime('%Y%m%d')}" + " " + f"{datetime.now().strftime('%H%M%S')}" + '\n' + \
                          my_note + '\n' + f"{axis}")


'''sweep temp from temp now to the 80K at rate = 1K/10min'''
target_value_temp = 80
delaytime = 50
step_size = 0.1
num_steps = int(np.floor(abs(target_value_temp) / (step_size))) + 1
pid.read()
t1()
k = 0
data = Mydata()
# initialize(keithley2400_gpib)
# output_on(keithley2400_gpib)
file_name = f"temp.txt"
title = ''
for val in np.linspace(float(pid.reading), target_value_temp, num_steps):
    pid.setpoint = val
    if 20 < val <= 70:
        pid.manual_tune(newkp=20, newki=0.1, newkd=15)
    if val > 70:
        pid.manual_tune(newkp=337, newki=1.5, newkd=15)
    for i in range(0, delaytime * 2):
        data.update()
        time.sleep(0.4)
    # pid.readinglog = []
    # pid.timelog = []
    data.data_save(file_name=file_name)
    k += 1
file_name = f"bng_sweepup.002"
data.data_save(file_name=file_name)
plot_save(pid.timelog, pid.readinglog, k)

pid.close()
sys.exit()
