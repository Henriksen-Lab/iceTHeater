import pyvisa, time
import numpy as np
from datetime import datetime

from keysightN6700c import *
from Agilent_infiniVision import *
import matplotlib.pyplot as plt
import time, threading

step_size = 0.05
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
global time_log, vol_log, counter_log, order

time_log = []
vol_log =[70]
counter_log = [infiniVision_get_counter()]
order = 0

t_now = time.time()
time_log += [t_now]

def update():
    while True:
        global time_log, vol_log, counter_log, order
        for vol in np.linspace(start_voltage, end_voltage, number_of_steps):
            set_voltage('GPIB0::5::INSTR', vol)
            time_log += [time.time()]
            vol_log += [vol]
            counter_log += [infiniVision_get_counter()]
            time.sleep(0.1)
        for vol in np.linspace(end_voltage, start_voltage, number_of_steps):
            set_voltage('GPIB0::5::INSTR', vol)
            time_log += [time.time()]
            vol_log += [vol]
            counter_log += [infiniVision_get_counter()]
            time.sleep(0.1)
        np.savetxt(
            dir + '\\' + f'vol_log.{order}',
            np.column_stack((time_log,vol_log,counter_log)), delimiter='\t',
            header=f"{datetime.now().strftime('%Y%m%d')}" + '\n' + "time(s)\t\t\tvoltage(V)\t\t\tcounter(Hz)\t\t\t")
        order +=1
        print("data saved")

def plot():
    fg = plt.figure()
    plt.xlabel("time(s)")
    plt.ylabel("counter(Hz)")
    while True:
        plt.plot(float(time_log[-1]-t_now), float(counter_log[-1]), '.r')
        #plt.show()
        plt.pause(1)



t1 = threading.Thread(target=update)
t1.start()
plot()