# Written by Shilling Du 7/25/2022
import sys, os, time, threading, tkinter
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from decimal import Decimal

folder_path = os.getcwd()
if folder_path not in sys.path:
    sys.path.append(
        folder_path)  # easier to open driver files as long as Simple_DAQ.py is in the same folder with drivers
from arduino_communication import arduino_set, arduino_read, arduino_read_set, arduino_read_output, arduino_set_pid, arduino_read_pid

class Myinfo:
    def __init__(self):
        #Input the file dir and address here
        self.setpoint = 34
        self.dir = r'C:\Users\Osmium\Documents\GitHub\iceTHeater\NvCenter_heater\Data\Aug1PIDTuning'

        #Initialize the variables
        self.time_interval = 1
        self.reading = 0
        self.timenow =0
        self.timelog = []
        self.templog = []
        self.setpoint_read = 0
        self.Output_read = 0
        self.pid_value = ''
        self.pid_read = ''

    def read(self):
        self.reading = float(arduino_read(arduino_name=arduino_address))
        self.timenow = float(time.time())
        self.setpoint_read = float(arduino_read_set(arduino_name=arduino_address))
        self.Output_read = float(arduino_read_output(arduino_name=arduino_address))
        self.pid_read = str(arduino_read_pid(arduino_name=arduino_address))
        self.timelog += [self.timenow]
        self.templog += [self.reading]

    def write(self):
        if self.setpoint != 0:
            arduino_set(arduino_name=arduino_address, t=self.setpoint)

    def write_pid(self):
        if self.pid_value != '':
            arduino_set_pid(arduino_name=arduino_address, pid=self.pid_value)

    def run(self):
        fg = plt.figure()
        plt.xlabel("time(s)")
        plt.ylabel("Temp(K)")
        t_now = time.time()
        while update_flag:
            self.write()
            self.write_pid()
            self.read()
      #      print(time.asctime(time.localtime(time.time())), "\nTemp =", self.reading, "C", ", Set point =",
      #            self.setpoint_read, "C")
            print(f"Setpoint = {self.setpoint_read}C, Output = {self.Output_read}%, PID value = {self.pid_read}")
            plt.title(f"Setpoint = {self.setpoint_read}C, Output = {self.Output_read}%, PID value = {self.pid_read}")
            plt.plot(self.timenow - t_now, self.reading, '.r')
            plt.xlim([0, self.timenow - t_now + 1])
            plt.pause(0.5)
            time.sleep(self.time_interval)
            np.savetxt(
                pid.dir +'\\'+ 'temp.txt',
                np.column_stack(([a - self.timelog[0] for a in self.timelog], self.templog)), delimiter='\t',
                header=f"\Setpoint = {pid.setpoint_read}C, Output = {pid.Output_read}%, PID value = {pid.pid_read}"+ '\n'
                       +datetime.now().strftime('%Y%m%d') + '\n' + "time\t\t\ttemp\t\t\t")
            print("data saved")

    def run_single(self):
        t_now = time.time()
        self.write()
        self.write_pid()
        self.read()
        print(time.asctime(time.localtime(time.time())), "\nTemp =", self.reading, "C", ", Set point =", self.setpoint_read, "C")
        print(f"Setpoint = {self.setpoint_read}C, Output = {self.Output_read}%, PID value = {self.pid_read}")
        print('temp now is', self.reading)
        time.sleep(self.time_interval)



def plot_save(x, y, order):
    fg1 = plt.figure()
    plt.plot([a - x[0] for a in x], y,'.r')
    plt.xlabel('time(s)')
    plt.ylabel('Temp(K)')
    plt.title(f"Setpoint = {pid.setpoint_read}C, Output = {pid.Output_read}%, PID value = {pid.pid_read}")
    fg1.savefig(
        pid.dir + f"\Setpoint = {pid.setpoint_read}C, Output = {pid.Output_read}%, PID value = {pid.pid_read}.{order}.jpg",
        bbox_inches='tight', dpi=150)
    plt.close()
    print("graph saved")
    np.savetxt(pid.dir + f"\Setpoint = {pid.setpoint_read}C, Output = {pid.Output_read}%, PID value = {pid.pid_read}.{order}",
               np.column_stack(([a - x[0] for a in x], y)), delimiter='\t',
               header= datetime.now().strftime('%Y%m%d')+ '\n' + "time\t\t\ttemp\t\t\t")
    print("data saved")
    time.sleep(0.1)


def pop_window():
    window = tkinter.Tk()
    window.title('Set temp')
    window.geometry('500x300')
    tkinter.Label(window, text='Input set temperature', height=2).pack()
    entry = tkinter.Entry(window)
    entry.pack()
    global update_flag
    update_flag = True
    t1()

    def on_click():
        value = entry.get()
        pid.setpoint = Decimal(float(value)).quantize(Decimal("0.00"))
        print("Set point = " + str(pid.setpoint) + "C")
        time.sleep(1)
        # window.destroy()

    tkinter.Button(window, text="Input", command=on_click).pack()
    tkinter.Label(window, text="Plese input pid values you want to change, in format k1.0p, meaning kp = 1.0", height=2).pack()
    entry_2 = tkinter.Entry(window)
    entry_2.pack()

    def on_click_2():
        value = entry_2.get()
        pid.pid_value = str(value)
        print("Set pid = " + str(pid.pid_value) + "")
        time.sleep(1)
        # window.destroy()

    tkinter.Button(window, text="Input", command=on_click_2).pack()

    def exit():
        global update_flag
        update_flag = False
        time.sleep(1)
        sys.exit()

    tkinter.Label(window, text="Plese press here to Exit", height=2).pack()
    tkinter.Button(window, text="Exit", command=exit).pack()
    window.mainloop()


def t1():
    t1 = threading.Thread(target=pid.run)
    t1.start()


'''-------------------------------------------------------MAIN----------------------------------------------------------'''
arduino_address = 'COM10'
pid = Myinfo()
''' if you want to do it manually'''

pop_window() # if you want to run it continuously and want change temp during the process, run this pop window func

''' if you want to tune single parameter and have your graph and data saved'''
''''''
for kp in np.linspace(1.30,1.31,num=1):
    pid.pid_value = 'k'+str(kp)+'p'

    for t in range (0,30*30):
        time.sleep(0.1)
        pid.run_single()
    plot_save(pid.timelog, pid.templog, kp)
    pid.timelog = []
    pid.templog = []
''''''