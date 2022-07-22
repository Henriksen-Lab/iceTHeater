# iceTHeater

Heater program for the IceT system

# updated by shilling Du on 7/22/2022
# In iceTHeater_old folder, PID controll is basing on arduino libary and the communication to keithley instrument is basing on a PROLOGIX gpib-USB controller, which has an outdated driver, so I re-write the program in new folder, iceTHeater-noise
# In iceTHeater_noise folder:
	for instrument communication:
		hp34461A(working for 34461A DMM)
		keithley_2400(working for keithley2400 and keithley2000)
		Arduino_control(for sending serial to arduino board)
	other functions:
		cernox(for converting resistance to temp)
	Main program:
		Simple DAQ_sweep_gate_for_lyw (no PID controll, only sweeping the output voltage)
		noise_probe_PID (standard PID controll method)
		noise_probe_IncrementPID (Increment PID controll method)
to be update...
