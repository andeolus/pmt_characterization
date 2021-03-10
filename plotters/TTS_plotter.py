import re
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Variables
datadir='TS0340_09sep/' # TS0340_09sep or R5900U_08sep or PMTECAL_15sep
print(datadir)
cfd_frac= 0.5
window='whole' # 'whole' / sregion16.5x16.5 / sregion15x15
print(window)

# Import data using pandas and sort it so it can be plotted

DF = pd.read_csv(datadir+'TTS_wma.txt', sep=" ") #TTS

# apply cuts:
# DF=DF.loc[DF['CFD_threshold_fraction'] == cfd_frac]
# DF=DF.loc[DF['X'] != -4.5].loc[DF['X'] != 15].loc[DF['Y'] != -19.5].loc[DF['Y'] != 0] #DF.loc[DF['Y'] == -1.5]
# if window == 'sregion16.5x16.5':
#     xmin,xmax,ymin,ymax=-3.,13.5,-18,-1.5 #-3.+1.5,13.5,-18,-1.5-1.5
#     DF= DF.loc[ (DF['X'] >= xmin) & (DF['X'] <= xmax ) & (DF['Y'] >= ymin) & (DF['Y'] <= ymax)]
# elif window == 'sregion15x15':
#     xmin,xmax,ymin,ymax= -3, 12, -16.5, -1.5 #<-TS  # nonTS:-3.+1.5,13.5,-18,-1.5-1.5
#     DF= DF.loc[ (DF['X'] >= xmin) & (DF['X'] <= xmax ) & (DF['Y'] >= ymin) & (DF['Y'] <= ymax)]

X_unique = np.sort(DF.X.unique())
Y_unique = np.sort(DF.Y.unique())
TOA_table=DF.pivot_table(index='X', columns='Y', values='mean').T.values # 'mean' or 'stddev' or 'maxVmean'
unc=DF.pivot_table(index='X', columns='Y', values='stddev').T.values # 'mean' or 'stddev' or 'maxVmean'
ampl=DF.pivot_table(index='X', columns='Y', values='maxVmean').T.values # 'mean' or 'stddev' or 'maxVmean'



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
plt.savefig("TTS_TOA_CFD_50_"+window+".png") # TOA / meanAmplitude / Uncertainties
plt.show()

# Plot time Uncertainties
fig, ax = plt.subplots()
title= "Time uncertainty [ns],  at {}% threshold".format(cfd_frac*100) # Mean time of arrival [ns] / Standard deviation Time uncertainty [ns] / Mean waveform amplitude [mV]
plt.title(title)
c = plt.imshow(unc,cmap='hot') # (1,2,3,4),(3,4,5,6),(1,2,1,2) # ,vmin=58.9, vmax=59.1 ,origin='upper' ,vmin=51
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
plt.savefig("TTS_Uncertainties_CFD_50_"+window+".png") # TOA / meanAmplitude / Uncertainties
plt.show()

# Pot Amplitudes
fig, ax = plt.subplots()
title= "Mean waveform amplitude [mV],  at {}% threshold".format(cfd_frac*100) # Mean time of arrival [ns] / Standard deviation Time uncertainty [ns] / Mean waveform amplitude [mV]
plt.title(title)
c = plt.imshow(ampl,cmap='hot') # (1,2,3,4),(3,4,5,6),(1,2,1,2) # ,vmin=58.9, vmax=59.1 ,origin='upper' ,vmin=51
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
plt.savefig("TTS_meanAmplitude_CFD_50_"+window+".png") # TOA / meanAmplitude / Uncertainties
plt.show()



DF=DF.sort_values(by=['X','Y'])
# Plot Errorbars
labels=[str(X)+','+str(Y) for X,Y in zip(DF['X'],DF['Y'])]
fig, ax = plt.subplots()
plt.title("Mean time of arrival")
plt.errorbar(range(len(DF['mean'].values)), DF['mean'].values, xerr=0, yerr=DF['stddev'].values,marker='x',ls='', capsize=1) #DF['stddev'].values
plt.xticks( np.arange(len(DF['mean'].values)) , labels ,rotation='vertical')
plt.xlabel('X,Y [mm]')
plt.ylabel('Time [ns]')
plt.xticks(fontsize=4, rotation=45)
fig.tight_layout()
plt.savefig("TTS_TOAwebars_CFD_50_"+window+".png", dpi=1200) # TOA / meanAmplitude / Uncertainties // _sregion
plt.show()

calcTotalStddev= lambda means,stds: (1/len(means)*sum(si**2+mi**2 for (si,mi) in zip(stds,means)) -(means.mean())**2 )**0.5
cstd=calcTotalStddev(DF['mean'].values,DF['stddev'].values)
stds=DF['stddev'].values
means=DF['mean'].values
# cstd= (1/len(means)*sum(si**2+mi**2 for (si,mi) in zip(stds,means)) -(means.mean())**2 )**0.5
# print('min std: ',min(stds),'\nmean std: ', np.mean(stds), '\nmax std: ', max(stds), '\ntotal std: ',cstd )
print('cfd: {}\nmin std: {:.3f}\nmean std: {:.3f}\nmax std: {:.3f}\ntotal std: {:.3f}'.format(cfd_frac,min(stds),np.mean(stds), max(stds),cstd ))
print('mean time: {:.3f},'.format(means.mean()))
