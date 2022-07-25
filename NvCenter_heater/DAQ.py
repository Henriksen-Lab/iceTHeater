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
from arduino_communication import arduino_set, arduino_read, arduino_read_set, arduino_read_output

class Myinfo:
    def __init__(self):
        #Input the file dir and address here
        self.setpoint = 30.00
        self.dir = r'C:\Users\Osmium\Documents\GitHub\iceTHeater\NvCenter_heater\Data'

        #Initialize the variables
        self.time_interval = 1
        self.reading = 0
        self.timenow =0
        self.timelog = []
        self.templog = []
        self.setpoint_read = 0
        self.Output_read = 0

    def read(self):
        self.reading = float(arduino_read(arduino_name=arduino_address))
        self.timenow = float(time.time())
        self.setpoint_read = float(arduino_read_set(arduino_name=arduino_address))
        self.Output_read = float(arduino_read_output(arduino_name=arduino_address))
        self.timelog += [self.timenow]
        self.templog += [self.reading]

    def write(self):
        arduino_set(arduino_name=arduino_address, t=self.setpoint)

    def run(self):
        fg = plt.figure()
        plt.xlabel("time(s)")
        plt.ylabel("Temp(K)")
        t_now = time.time()
        while update_flag:
            self.read()
            self.write()
            print(time.asctime(time.localtime(time.time())), "\nTemp =", self.reading, "C", ", Set point =",
                  self.setpoint_read, "C")
            plt.title(f"Setpoint = {pid.setpoint_read}C, Output = {self.Output_read}%")
            plt.plot(self.timenow - t_now, self.reading, '.r')
            plt.xlim([0, self.timenow - t_now + 1])
            plt.pause(0.5)
            time.sleep(self.time_interval)


def plot_save(x, y, order):
    fg1 = plt.figure()
    plt.plot([a - x[0] for a in x], y)
    plt.xlabel('time(s)')
    plt.ylabel('Temp(K)')
    plt.title(f"setpoint = {pid.setpoint}C")
    fg1.savefig(
        pid.dir + f"/setpoint_{pid.setpoint}C"+ f'_{order}.jpg',
        bbox_inches='tight', dpi=150)
    plt.close()
    print("graph saved")
    np.savetxt(pid.dir + f"/setpoint_{pid.setpoint}C"+ f'.{order}',
               np.column_stack(([a - x[0] for a in x], y)), delimiter='\t',
               header= datetime.now().strftime('%Y%m%d')+ '\n' + "time\t\t\ttemp\t\t\t")
    print("data saved")
    time.sleep(0.1)


def pop_window():
    window = tkinter.Tk()
    window.title('Set temp')
    window.geometry('300x200')
    tkinter.Label(window, text='Input set temperature', height=2).pack()
    entry = tkinter.Entry(window)
    entry.pack()
    global update_flag
    update_flag = True
    t1()

    def on_click():
        value = entry.get()
        pid.setpoint = Decimal(float(value)).quantize(Decimal("0.00"))
        pid.write()
        print("Set point = " + str(pid.setpoint) + "C")
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
    t1 = threading.Thread(target=pid.run)
    t1.start()


'''-------------------------------------------------------MAIN----------------------------------------------------------'''
arduino_address = 'COM10'
pid = Myinfo()
#pop_window() # if you want to run it continuously and want change temp during the process, run this pop window func
update_flag = True
pid.run()
