# -*- coding: utf-8 -*-
"""
Created on Tues Feb 8 16:17:58 2022

@author: Shilling Du
@date: Feb 8, 2022
"""

import numpy as np
from datetime import datetime
import time, sys, os, pyvisa

folder_path = os.getcwd()
if folder_path not in sys.path:
    sys.path.append(folder_path) # easier to open driver files as long as Simple_DAQ.py is in the same folder with drivers
    #from vna_analysis import get_smith_data, change_vna_settings
from SR830 import SR830_get_x, SR830_get_y
from keithley_2400 import set_voltage_V, get_voltage_2000, initialize, output_on
from hp34471A import get_voltage_hp34461a

rm = pyvisa.ResourceManager()
'''---------------------INPUT BEFORE RUN---------------------'''
#SR830_gpib_1 = 'GPIB0::5::INSTR'
#SR830_gpib_2 = 'GPIB0::6::INSTR'
keithley2400_gpib = 'GPIB0::25::INSTR'
keithley2000_gpib = 'GPIB0::18::INSTR'
hp34461a = 'GPIB0::17::INSTR'
data_dir = r"C:\Users\ICET\Desktop\Data\lyw"
my_note = "2022.07.02 Icet bn-g-bn capcitively coupled device test"
# tell me about your exp, start a new line by \n
list = ['timestamp', 'V_T_x', 'V_T_y', 'I_T_x', 'I_T_y', 'V_diode','V_heater']

# customized



target_value_V = 4.5
step_size_V = 0.00015
delaytime = 1

'''---------------------Start run---------------------'''
num_steps = int(np.floor(abs(target_value_V) / (step_size_V))) + 1

title = "_" + "sweepUP" # some unique feature you want to add in title
timestamp=[]; V_T_x=[]; V_T_y=[]; I_T_x=[]; I_T_y=[]; V_diode=[]; V_heater=[]
order = 1
axis = ''
for x in list:
    axis += f"{x}_{order}\t\t\t"
for val in np.linspace(0, target_value_V, num_steps):
    set_voltage_V(keithley2400_gpib, val)
    print("sweep voltage to: ", val)
    time.sleep(delaytime)
    print("reads: ", get_voltage_2000(keithley2000_gpib))
    timestamp += [time.time()]
    V_T_x += [SR830_get_x(SR830_gpib_1)]
    V_T_y += [SR830_get_y(SR830_gpib_1)]
    I_T_x += [SR830_get_x(SR830_gpib_2)]
    I_T_y += [SR830_get_y(SR830_gpib_2)]
    V_diode_reading = get_voltage_hp34461a(hp34461a)
    V_diode += [V_diode_reading]
    V_heater += [get_voltage_2000(keithley2000_gpib)]
    print("diode reads: ", V_diode_reading)
file_name = f"bngbn_sweep_up.001"
data = np.column_stack((timestamp, V_T_x, V_T_y, I_T_x, I_T_y, V_diode, V_heater))
os.makedirs(data_dir + '\\' + datetime.now().strftime('%Y%m%d')+ title, exist_ok=True)
np.savetxt(data_dir + '\\' + datetime.now().strftime('%Y%m%d')+ title + "/" + file_name, data, delimiter='\t',
               header = f"{datetime.now().strftime('%Y%m%d')}"+" "+f"{datetime.now().strftime('%H%M%S')}"+'\n'+ \
                   my_note + '\n'+ f"{axis}")
print("Sweep up ok")
time.sleep(300)



title = "_" + "sweepDown" # some unique feature you want to add in title
timestamp=[]; V_T_x=[]; V_T_y=[]; I_T_x=[]; I_T_y=[]; V_diode=[]; V_heater=[]
order = 1
axis = ''
for x in list:
    axis += f"{x}_{order}\t\t\t"
for val in np.linspace(target_value_V, 0, num_steps):
    set_voltage_V(keithley2400_gpib, val)
    print("sweep voltage to: ", val)
    time.sleep(delaytime)
    print("reads: ", get_voltage_2000(keithley2000_gpib))
    timestamp += [time.time()]
    V_T_x += [SR830_get_x(SR830_gpib_1)]
    V_T_y += [SR830_get_y(SR830_gpib_1)]
    I_T_x += [SR830_get_x(SR830_gpib_2)]
    I_T_y += [SR830_get_y(SR830_gpib_2)]
    V_diode_reading = get_voltage_hp34461a(hp34461a)
    V_diode += [V_diode_reading]
    V_heater += [get_voltage_2000(keithley2000_gpib)]
    print("diode reads: ", V_diode_reading)
file_name = f"bngbn_sweep_down.001"
data = np.column_stack((timestamp, V_T_x, V_T_y, I_T_x, I_T_y, V_diode, V_heater))
os.makedirs(data_dir + '\\' + datetime.now().strftime('%Y%m%d') + title, exist_ok=True)
np.savetxt(data_dir + '\\' + datetime.now().strftime('%Y%m%d') + title + "/" + file_name, data, delimiter='\t',
           header=f"{datetime.now().strftime('%Y%m%d')}" + " " + f"{datetime.now().strftime('%H%M%S')}" + '\n' + \
                  my_note + '\n' + f"{axis}")
print("Sweep down ok")

set_voltage_V(keithley2400_gpib, 0)



