# -*- coding: utf-8 -*-
"""
Created on Sat July 2 2022

@author: shilling

"""

import numpy as np
import pyvisa
import time

rm = pyvisa.ResourceManager()

def get_voltage_hp34461a(address):
    try:
        with rm.open_resource(address) as hp34461a:
            hp34461a.write("SENS:FUNC \'volt:DC\'") # set volt
            hp34461a.write("SENS:volt:dc:RANG:AUTO ON") # Auto range
            string_data = hp34461a.query("READ?")
            numerical_data = float(string_data)
    finally:
        hp34461a.close()
    return numerical_data

print(get_voltage_hp34461a('GPIB0::17::INSTR'))