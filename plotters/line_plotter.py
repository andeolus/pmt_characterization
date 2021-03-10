import re
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Variables
cfd_frac= 0.5

# Import data using pandas and sort it so it can be plotted
DF = pd.read_csv('TTS_wma.txt', sep=" ") #TTS
# DF=DF.loc[DF['CFD_threshold_fraction'] == cfd_frac]
# DF=DF.loc[DF['X'] != 0]
# DF=DF.loc[DF['Y'] != 3]
# DF=DF.loc[DF['X'] != 18]
# DF=DF.loc[DF['Y'] != -15]
# DF=DF.loc[-19.5<DF['Y']<0]
# DF=DF.loc[-4.5<DF['X']<15]
# DF=DF.loc[DF['X'] != -4.5].loc[DF['X'] != 15].loc[DF['Y'] != -19.5].loc[DF['Y'] != 0]
X_unique = np.sort(DF.X.unique())
Y_unique = np.sort(DF.Y.unique())
TOA_table=DF.pivot_table(index='X', columns='Y', values='mean').T.values # 'mean' or 'stddev' or 'maxVmean'
unc=DF.pivot_table(index='X', columns='Y', values='stddev').T.values # 'mean' or 'stddev' or 'maxVmean'
ampl=DF.pivot_table(index='X', columns='Y', values='maxVmean').T.values # 'mean' or 'stddev' or 'maxVmean'

llist= [(a,b) for a,b in zip(DF['X'].values,DF['maxVmean'].values)]
llist=sorted( llist , key = lambda x: x[0])
xlist= [x for x,_ in llist]
alist= [a for _,a in llist]

# Pot Amplitudes
fig, ax = plt.subplots()
title= "Mean waveform amplitude [mV]"
plt.title(title)
plt.plot(xlist,alist,'x-') #DF['X'].values,DF['maxVmean'].values
# ax.set_xticks(np.arange(len(X_unique)))
# ax.set_yticks(np.arange(len(Y_unique)))
# ax.set_xticklabels(X_unique)
# ax.set_yticklabels(Y_unique)
# ax.set_ylim( bottom=len(Y_unique)-0.5, top=-0.5, emit=True, auto=False, ymin=None, ymax=None)
# ax.invert_yaxis()
# # Add lables to each point
# for i in range(len(X_unique)):
#     for j in range(len(Y_unique)):
#         text = ax.text(j, i, str(TOA_table[i, j].round(3))+'\n±'+str(unc[i, j].round(3)), #3 / 0
#                        ha="center", va="center", color="gray")
# plt.text(0.05, 0.95,'std: '+str(fracTs_jitter)+ ' ns', transform=ax.transAxes)
plt.xlabel('X  [mm]')
plt.ylabel('Amplitude [mV]')
fig.tight_layout()
plt.savefig("TTS_Line_Amplitude.png") # TOA / meanAmplitude / Uncertainties
plt.show()



'''
# Plot TOAs
fig, ax = plt.subplots()
title= "Mean time of arrival [ns],  at {}% threshold".format(cfd_frac*100) # Mean time of arrival [ns] / Standard deviation Time uncertainty [ns] / Mean waveform amplitude [mV]
plt.title(title)
c = plt.imshow(TOA_table,cmap='hot') # (1,2,3,4),(3,4,5,6),(1,2,1,2) # ,vmin=58.9, vmax=59.1 ,origin='upper' ,vmin=51
plt.colorbar(c)
ax.set_xticks(np.arange(len(X_unique)))
ax.set_yticks(np.arange(len(Y_unique)))
ax.set_xticklabels(X_unique)
ax.set_yticklabels(Y_unique)
ax.set_ylim( bottom=len(Y_unique)-0.5, top=-0.5, emit=True, auto=False, ymin=None, ymax=None)
ax.invert_yaxis()
# # Add lables to each point
# for i in range(len(X_unique)):
#     for j in range(len(Y_unique)):
#         text = ax.text(j, i, str(TOA_table[i, j].round(3))+'\n±'+str(unc[i, j].round(3)), #3 / 0
#                        ha="center", va="center", color="gray")
# plt.text(0.05, 0.95,'std: '+str(fracTs_jitter)+ ' ns', transform=ax.transAxes)
plt.xlabel('X  [mm]')
plt.ylabel('Y [mm]')
fig.tight_layout()
plt.savefig("TTS_TOA_CFD_50_sregion.png") # TOA / meanAmplitude / Uncertainties
plt.show()
'''
