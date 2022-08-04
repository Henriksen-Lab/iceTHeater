# Written by Shilling Du 8/4/2022

import pyvisa, time
import numpy as np
from datetime import datetime

rm = pyvisa.ResourceManager()

def set_voltage(address,target_value_V):
    try:
        keysight6700 = rm.open_resource(address)
        #keysight6700.write("sour:volt:rang:auto 1")
        keysight6700.write(f"sour:volt {target_value_V},(@2)")
    finally:
        keysight6700.close()

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
time_log = []
vol_log =[]
while True:
    for vol in np.linspace(start_voltage, end_voltage, number_of_steps):
        set_voltage('GPIB0::5::INSTR', vol)
        time_log += [time.time()]
        vol_log += [vol]
        time.sleep(0.1)
    for vol in np.linspace(end_voltage, start_voltage, number_of_steps):
        set_voltage('GPIB0::5::INSTR', vol)
        time.sleep(0.1)
        time_log += [time.time()]
        vol_log += [vol]
    np.savetxt(
        dir + '\\' + 'vol_log.txt',
        np.column_stack((time_log,vol_log)), delimiter='\t',
        header=f"{datetime.now().strftime('%Y%m%d')}" + '\n' + "time\t\t\tvoltage\t\t\t")
    print("data saved")