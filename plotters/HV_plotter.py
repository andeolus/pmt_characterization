import re
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Variables
cfd_frac= 0.5

# Import data using pandas and sort it so it can be plotted
DF = pd.read_csv('TTS.txt', sep=" ") #TTS
DF=DF.sort_values(by=['HV'])

# Pot Amplitudes
fig, ax = plt.subplots()
title= "Amplitude vs HV"
plt.title(title)
plt.plot(DF['HV'].values,DF['maxVmean'].values,'x-') #DF['X'].values,DF['maxVmean'].values
plt.xlabel('High Voltage [V]')
plt.ylabel('Amplitude [mV]')
# plt.xscale('log')
plt.yscale('log')
fig.tight_layout()
plt.savefig("TTS_AvsHV_logscale.png") # TOA / meanAmplitude / Uncertainties
plt.show()

# DF=DF.loc[DF.HV!=400]

# Pot Times
fig, ax = plt.subplots()
title= "Time vs HV"
plt.title(title)
# plt.plot(DF['HV'].values,DF['mean'].values,'x') #DF['X'].values,DF['maxVmean'].values
plt.errorbar(DF['HV'].values,DF['mean'].values,yerr=DF['stddev'].values,capsize=4,linestyle='')
plt.xlabel('High Voltage [V]')
plt.ylabel('Time of arrival [ns]')
fig.tight_layout()
plt.savefig("TTS_TOAvsHV.png") # TOA / meanAmplitude / Uncertainties
plt.show()


fig, ax = plt.subplots()
title= "Time uncertainty vs HV"
plt.title(title)
# plt.plot(DF['HV'].values,DF['mean'].values,'x') #DF['X'].values,DF['maxVmean'].values
plt.plot(DF['HV'].values,DF['stddev'].values,'x')
plt.xlabel('High Voltage [V]')
plt.ylabel('Time uncertainty [ns]')
fig.tight_layout()
plt.savefig("TTS_TOAuncertaintyvsHV.png") # TOA / meanAmplitude / Uncertainties
plt.show()


# print(DF)
# DF['Gain']=DF['Gain']*1250/50

# Plot Gain and Gain2
fig, ax = plt.subplots()
title= "Gain vs HV"
plt.title(title)
# plt.plot(DF['HV'].values,DF['mean'].values,'x') #DF['X'].values,DF['maxVmean'].values
plt.plot(DF['HV'].values,DF['Gain'].values,'x')
plt.xlabel('High Voltage [V]')
plt.ylabel('Gain')
plt.xscale('log')
plt.yscale('log')
plt.grid(True,'both')
plt.grid(True,'minor','y',linestyle='--',linewidth=0.5)
fig.tight_layout()
plt.savefig("TTS_GainvsHV50.png") # TOA / meanAmplitude / Uncertainties
plt.show()


fig, ax = plt.subplots()
title= "Gain vs HV"
plt.title(title)
# plt.plot(DF['HV'].values,DF['mean'].values,'x') #DF['X'].values,DF['maxVmean'].values
plt.plot(DF['HV'].values,DF['Gain2'].values,'x')
plt.xlabel('High Voltage [V]')
plt.ylabel('Gain')
plt.xscale('log')
plt.yscale('log')
plt.grid(True,'both')
plt.grid(True,'minor','y',linestyle='--',linewidth=0.5)
fig.tight_layout()
plt.savefig("TTS_Gainvs2HV50.png") # TOA / meanAmplitude / Uncertainties
plt.show()
