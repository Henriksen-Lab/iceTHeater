# -*- coding: utf-8 -*-
"""
Created on Tue Sep  1 22:18:28 2020

@author: Crow108

@revised: Shilling Du 02092020 11:24
=======
@revised: Shilling Du 02092020 11:24 added function get_ohm_4pt

"""

import numpy as np
import pyvisa
import time

rm = pyvisa.ResourceManager()

def initialize(address):
    try:
        keithley = rm.open_resource(address)
        keithley.write("*RST")
        keithley.write("status:preset")
        keithley.write("*cls")
        print("keithley initialized: ", address)
    finally:
        keithley.close()

def output_on(address):
    try:
        keithley = rm.open_resource(address)
        keithley.write("OUTP ON")
        keithley.write("SENS:CURR:PROT MAX")
        keithley.write("SYST:KEY 23")
        print("keithley out put on")
    finally:
        keithley.close()

def ramp_from_prev_value_I(address, target_value_mA, step_size_mA=0.01):
    try:
        keithley = rm.open_resource(address)            
        last_value_mA = float( keithley.query("sour:curr?") )*1000
        
        num_steps = int(np.floor( abs((last_value_mA - target_value_mA))/ (step_size_mA))) +1
        # arange excludes last point; so use linspace
        for val in np.linspace(last_value_mA, target_value_mA, num_steps):
            keithley.write(f"sour:curr {np.round(val*1E-3,6)}")
    finally:     
        keithley.close()            
        
def get_sur_currrent_A(address):
    try:
        keithley = rm.open_resource(address)            
        last_value_A = float( keithley.query("sour:curr?") )
    finally:     
        keithley.close()       
    return last_value_A


def ramp_from_prev_value_V(address, target_value_V, step_size_V=0.00025, delaytime= 2):
    try:
        keithley = rm.open_resource(address)
        last_value_V = float(keithley.query("sour:volt?"))

        num_steps = int(np.floor(abs((last_value_V - target_value_V)) / (step_size_V))) + 1
        # arange excludes last point; so use linspace
        for val in np.linspace(last_value_V, target_value_V, num_steps):
            keithley.write(f"sour:volt {np.round(val, 6)}")
            time.sleep(delaytime)
    finally:
        keithley.close()


def get_sur_voltage_V(address):
    try:
        keithley = rm.open_resource(address)
        last_value_V = float(keithley.query("sour:volt?"))
    finally:
        keithley.close()
    return last_value_V

def set_voltage_V(address, target_value_V):
    try:
        keithley = rm.open_resource(address)
        keithley.write("sour:func volt")
        keithley.write("sour:volt:rang:auto 1")
        keithley.write(f"sour:volt {target_value_V}")
    finally:
        keithley.close()

def get_ohm_4pt_2000(address):
    try:
        keithley = rm.open_resource(address)
        keithley.write("SENS:FUNC \"FRES\"") # measure 4 wire Resistance for 2000
        keithley.write("SENS:FRES:RANG:AUTO 1") # Auto range
        keithley.write("FORM:ELEM FRES") # only output R
        string_data = keithley.query("READ?")

        numerical_data = float(string_data)
    finally:     
        keithley.close()
    return numerical_data

def get_ohm_2pt_2400(address):
    try:
        keithley = rm.open_resource(address)
        keithley.write("SENS:FUNC 'RES'") # measure Resistance
        keithley.write("RES:MODE AUTO") # mode: auto
        keithley.write("SYST:RSEN ON")  # set to 4 wire sensing
        keithley.write("SENS:RES:RANG:AUTO 1") # Auto range
        keithley.write("FORM:ELEM RES") # only output R
        string_data = keithley.query("READ?")
        numerical_data = float(string_data)
    finally:
        keithley.close()
    return numerical_data

def get_voltage_keithley(address):
    try:
        keithley = rm.open_resource(address)
        keithley.write("SENS:FUNC \'volt\'") # set volt
        keithley.write("SENS:volt:RANG:AUTO 1") # Auto range
        keithley.write("FORM:ELEM VOLT")
        string_data = keithley.query("READ?")
        numerical_data = float(string_data)
    finally:
        keithley.close()
    return numerical_data

print(get_voltage_keithley('GPIB0::25::INSTR'))
