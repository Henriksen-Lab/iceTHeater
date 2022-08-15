import pyvisa, time
import numpy as np
from datetime import datetime

from keysightN6700c import *
from Agilent_infiniVision import *
from hp34461A import *
import matplotlib.pyplot as plt
import time, threading

step_size = 0.005
start_voltage = 70
end_voltage = 80
number_of_steps = int(np.floor(abs(end_voltage-start_voltage)/step_size))+1
dir = r'C:\Users\Osmium\Documents\GitHub\iceTHeater\NvCenter_heater\Data\voltage sweeping'

'''
#for single sweep up
for vol in np.linspace(start_voltage,end_voltage, number_of_steps):
    set_voltage('GPIB0::5::INSTR',vol)
    time.sleep(0.1)
'''
# for continuously sweeping up and down
global time_log, sur_vol_log, counter_log,read_vol_log, order

time_log = []
sur_vol_log = []
read_vol_log = []
counter_log = []
order = 0

t_now = time.time()


def update():
    while True:
        global time_log, sur_vol_log, counter_log, order, read_vol_log
        for vol in np.linspace(start_voltage, end_voltage, number_of_steps):
            set_voltage('GPIB0::5::INSTR', vol)
            sur_vol_log += [vol]
            counter_log += [infiniVision_get_counter()]
            read_vol_log += [get_voltage_hp34461a('GPIB0::16::INSTR')]
            time_log += [time.time()]
            time.sleep(0.1)
        for vol in np.linspace(end_voltage, start_voltage, number_of_steps):
            set_voltage('GPIB0::5::INSTR', vol)
            sur_vol_log += [vol]
            counter_log += [infiniVision_get_counter()]
            read_vol_log += [get_voltage_hp34461a('GPIB0::16::INSTR')]
            time_log += [time.time()]
            time.sleep(0.1)
        np.savetxt(
            dir + '\\' + f'sur_vol_log.{order}',
            np.column_stack((time_log,sur_vol_log,read_vol_log,counter_log)), delimiter='\t',
            header=f"{datetime.now().strftime('%Y%m%d')}" + '\n' + "time(s)\t\t\tsupply_voltage(V)\t\t\tread_voltage(V)\t\t\tcounter(Hz)\t\t\t")
        order +=1
        print("data saved")

def plot():
    fg = plt.figure()
    gs = fg.add_gridspec(1, 2, width_ratios=[1, 0])
    ax = fg.add_subplot(gs[0])
    ax.set_xlabel("time(s)")
    ax.set_ylabel("counter(Hz)")
    # plot another line that share the same x axis
    ax1 = ax.twinx()
    ax1.set_ylabel('read voltage')

    while True:
        length = min(len(time_log),len(read_vol_log),len(counter_log))-1
        ax1.plot([a- t_now for a in np.array(time_log)][-length:], np.array(read_vol_log)[-length:], '.b')
        ax.plot([a- t_now for a in np.array(time_log)][-length:], np.array(counter_log)[-length:], '.r')

        plt.pause(0.5)



t1 = threading.Thread(target=update)
t1.start()
plot()