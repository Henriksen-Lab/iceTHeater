# Written by Shilling Du 8/11/2022

import pyvisa, time
import numpy as np
from datetime import datetime

rm = pyvisa.ResourceManager()

def infiniVision_get_counter(address= 'USB0::0x0957::0x1790::MY54230292::INSTR'):
    try:
        infiniVision = rm.open_resource(address)
        infiniVision.write(":MEASure:CLEar")
        string_data = infiniVision.query(":MEASure:COUNter?")
        numerical_data = float(string_data)
    finally:
        infiniVision.close()
    return numerical_data
