import argparse
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# Plot TT
def plot_TT(TT_table, X_unique, Y_unique, cfd_frac, window_name):
    fig, ax = plt.subplots()
    title= "Mean transit time [ns],  at {}% CFD threshold".format(cfd_frac*100)
    plt.title(title)
    c = plt.imshow(TT_table,cmap='hot') # (1,2,3,4),(3,4,5,6),(1,2,1,2) # ,vmin=58.9, vmax=59.1 ,origin='upper' ,vmin=51
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
    plt.xlabel('X [mm]')
    plt.ylabel('Y [mm]')
    fig.tight_layout()
    if window_name != "":
        window_name = "_"+window_name
    plt.savefig( "TT_CFD{}{}.png".format(cfd_frac*100,window_name) )
    plt.show()

# Plot TTS
def plot_TTS(TTS_table, X_unique, Y_unique, cfd_frac, window_name):
    fig, ax = plt.subplots()
    title= "Transit time spread [ns],  at {}% CFD threshold".format(cfd_frac*100) # Mean time of arrival [ns] / Standard deviation Time uncertainty [ns] / Mean waveform amplitude [mV]
    plt.title(title)
    c = plt.imshow(TTS_table,cmap='hot') # (1,2,3,4),(3,4,5,6),(1,2,1,2) # ,vmin=58.9, vmax=59.1 ,origin='upper' ,vmin=51
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
    plt.xlabel('X [mm]')
    plt.ylabel('Y [mm]')
    fig.tight_layout()
    if window_name != "":
        window_name = "_"+window_name
    plt.savefig( "TTS_CFD{}{}.png".format(cfd_frac*100,window_name) )
    plt.show()

# Pot Amplitudes
def plot_amplitudes(ampl, X_unique, Y_unique, cfd_frac, window_name):
    fig, ax = plt.subplots()
    title= "Mean waveform amplitude [mV]"
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
            # text = ax.text(j, i, str(ampl[i, j].round(3)), ha="center", va="center", color="gray")
    # plt.text(0.05, 0.95,' ', transform=ax.transAxes)
    plt.xlabel('X [mm]')
    plt.ylabel('Y [mm]')
    fig.tight_layout()
    if window_name != "":
        window_name = "_"+window_name
    plt.savefig( "mean_amplitude_CFD{}{}.png".format(cfd_frac*100,window_name) )
    plt.show()

def plot_errorbars(DF, window_name=''):
    DF=DF.sort_values(by=['X','Y'])
    # Plot Errorbars
    labels=[str(X)+','+str(Y) for X,Y in zip(DF['X'],DF['Y'])]
    fig, ax = plt.subplots()
    plt.title("Mean transit time")
    plt.errorbar(range(len(DF['mean'].values)), DF['mean'].values, xerr=0,
                yerr=DF['stddev'].values,marker='x',ls='', capsize=1) #DF['stddev'].values
    plt.xticks( np.arange(len(DF['mean'].values)) , labels ,rotation='vertical')
    plt.xlabel('X,Y [mm]')
    plt.ylabel('Time [ns]')
    plt.xticks(fontsize=4, rotation=45)
    fig.tight_layout()
    if window_name != "":
        window_name = "_"+window_name
    plt.savefig( "TTwithTTSerrorbars_CFD{}{}.png".format(cfd_frac*100,window_name), dpi=1200)
    plt.show()

def print_uniformity_info(DF):
    calcTotalStddev= lambda means,stds: (1/len(means)*sum(si**2+mi**2 for (si,mi) in zip(stds,means)) -(means.mean())**2 )**0.5
    cstd=calcTotalStddev(DF['mean'].values,DF['stddev'].values)
    stds=DF['stddev'].values
    means=DF['mean'].values
    # cstd= (1/len(means)*sum(si**2+mi**2 for (si,mi) in zip(stds,means)) -(means.mean())**2 )**0.5
    # print('min std: ',min(stds),'\nmean std: ', np.mean(stds), '\nmax std: ', max(stds), '\ntotal std: ',cstd )
    print('cfd: {}\nmin std: {:.3f}\nmean std: {:.3f}\nmax std: {:.3f}\ntotal std: {:.3f}'.format(cfd_frac,min(stds),np.mean(stds), max(stds),cstd ))
    print('mean time: {:.3f},'.format(means.mean()))

def make_plots(input_file="TTS.txt", cfd_frac=-1, cfd_cut=False, window=None, window_name="" ):
    DF = pd.read_csv(input_file, sep=" ") #TTS
    # apply cuts:
    if cfd_cut:
        DF=DF.loc[DF['CFD_threshold_fraction'] == cfd_frac]
    if window:
        xmin = window[0]
        xmax = window[1]
        ymin = window[2]
        ymax = window[3]
        DF= DF.loc[ (DF['X'] >= xmin) & (DF['X'] <= xmax ) & (DF['Y'] >= ymin) & (DF['Y'] <= ymax)]

    X_unique = np.sort(DF.X.unique())
    Y_unique = np.sort(DF.Y.unique())
    TT_table=  DF.pivot_table(index='X', columns='Y', values='mean').T.values
    TTS_table= DF.pivot_table(index='X', columns='Y', values='stddev').T.values
    ampl=      DF.pivot_table(index='X', columns='Y', values='maxVmean').T.values

    plot_TT( TT_table, X_unique, Y_unique, cfd_frac, window_name)
    plot_TTS( TTS_table, X_unique, Y_unique, cfd_frac, window_name)
    plot_amplitudes( ampl, X_unique, Y_unique, cfd_frac, window_name)
    plot_errorbars(DF, window_name)
    print_uniformity_info(DF)

# ------------------------------------------------------------------------


if __name__ == '__main__':
    ''' Plot trasient time, transit time spread and mean signal amplitude of a given PMT.
    needs the name of the input file containing the information, typically TTS.txt or TTS_wma.txt
    '''

    parser = argparse.ArgumentParser(
            description=
            ''' Plot trasient time, transit time spread and mean signal amplitude of a given PMT.
            needs the name of the input file containing the information, typically TTS.txt or TTS_wma.txt
            ''')
    parser.add_argument('input_file',     type=str,   nargs='?', default="TTS.txt",
            help='path [/name] of the file containing the analyzed data')
    parser.add_argument('--cfd_frac',     type=float, nargs='?', default=0.5,
            help='CFD threshold, default: 0.5')
    parser.add_argument('--cfd_cut',     type=float, nargs='?', default=False,
            help='apply cut to plot only the given CFD threshold (input file could contain more than one)')
    parser.add_argument('-w', '--window', type=float, nargs='*',
            help='restrict plot to a particular window of xmin xmax ymin ymax')
    parser.add_argument('-n', '--window_name', type=str, nargs='?', default="",
            help='name of the window you are plotting, eg: whole or region15x15') # 'whole' / sregion16.5x16.5 / sregion15x15
    args = parser.parse_args()

    # input file, window and CFD_threshold_fraction
    input_file = args.input_file # '' # TS0340_09sep/ or R5900U_08sep/ or PMTECAL_15sep/
    cfd_frac= args.cfd_frac # 0.5
    cfd_cut = args.cfd_cut # False
    window= args.window
    window_name = args.window_name
    print("plotting from: " , input_file )
    print("using window: ", window, " and CFD threshold at: ", 100*cfd_frac, "%")

    make_plots(input_file, cfd_frac, cfd_cut, window, window_name )
