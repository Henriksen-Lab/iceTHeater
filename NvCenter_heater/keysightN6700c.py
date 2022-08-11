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
