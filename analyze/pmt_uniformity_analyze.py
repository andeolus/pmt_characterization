# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import sys
import struct
import os.path
import getopt
import numpy as np
import re
import os
import argparse

def read_waveform( fd ):
    # Ponemos "h" o "H" en el unpack dependiendo de si usamos el MSO9404 o el MSOX3034A respectivamente
    #Asi como el wave_size con 40 o 36 siguiendo lo mismo de arriba
    header = struct.unpack( 4 * 'd' , fd.read( 4 * 8 ) )
    datatype = 'h'
    # print( "Header:", header)
    waveform_length = struct.unpack( 1 * 'i' , fd.read( 1 * 4 ) )[ 0 ]
    waveform = [ value * header[ 3 ] + header[ 2 ] for value in struct.unpack( int( waveform_length/2 ) * datatype, fd.read( waveform_length    ) ) ]
    wave_size = struct.calcsize(4*'d' + 'i' + waveform_length*datatype) # 40 + waveform_length*2
    # print( "Waveform length:", len( waveform ) )
    return header, waveform, wave_size

def calculate_pedestal( waveform, pedRange ):
    "Remove the hash key to visualize the piece of waveform used to calculate the pedestal."
    # pylab.plot( range( pedRange ), waveform[ : pedRange ] )
    # pylab.ylabel( "Pedestal" )
    # pylab.grid( True )
    return np.average( waveform[ : pedRange ] )

def calculate_charge( waveform, pedestal, xinc, cut_ini, cut_end ):
    "Remove the hash key to visualize the piece of waveform used to calculate the charge of the waveform."
    charge = 0
    wave_ped_subs = np.array( waveform ) - pedestal
    for it in range( cut_ini, cut_end - 1 ):
        charge += ( wave_ped_subs[ it ] + ( wave_ped_subs[ it + 1 ] - wave_ped_subs[ it ] ) / 2 ) * xinc / 1250    #Este 1250 es la resistencia corregida

    return charge

# "Mathematical" CFD, takes the closest value to f% of the total amplitude
def analyze_waveform(samples_PS, times, f, thr):
    peak_ampl = max(samples_PS)
    maxVIndex = np.argmax(samples_PS)
    peak_time = times[maxVIndex]
    fracIndex = (np.abs(samples_PS[:maxVIndex]-f*peak_ampl)).argmin()
    cfdTime = times[fracIndex]

    leIndex = (np.abs(samples_PS[:maxVIndex]-thr)).argmin()
    try:
        m,b = np.polyfit(times[leIndex-5:leIndex+5],samples_PS[leIndex-5:leIndex+5],1)
        leTime= (thr-b)/m
    except:
        print('error al fit, l100')
        leTime= 0
    # leTime_nointer = times[leIndex] # Leading edge time, no interpolation.
    return  peak_ampl, peak_time, cfdTime, leTime

# Electronically simulated CFD
def getCFDThreshold( times, waveform, xinc, points, attenuation=0, delay=0, threshold=0 ):
    ''' attenuation : db
        delay       : ns
        threshold     : V (minimum value)
    '''
    #Discard if there is no signal
    if max(waveform) < threshold and threshold > 0:
        return 0, []

    #Calculate offset in points
    delay = int(round(delay*1E-9/xinc))

    #Calculate the operation signal
    data  = np.array(waveform[:-delay])
    dummy = np.array(waveform[ delay:])*pow(10., -attenuation*0.1)
    resul = list(data - dummy) + [0]*(points-len(data))

    #Calculate the zero position
    max_ind = waveform.index(max(waveform))
    zero_ind = 0
    for i in range(max_ind)[::-1]:
        if resul[i] <= 0:
            zero_ind = i
            break

    #Calculate the threshold
    try:
        th = waveform[zero_ind] + (waveform[zero_ind+1] - waveform[zero_ind])*(0 - resul[zero_ind])/(resul[zero_ind+1] - resul[zero_ind])
        digitalData = list( np.int8(np.array(waveform) >= th) )
    except:
        th = 0
        print ( "ERROR> Could not calculate CFD" )
    '''
    plt.figure()
    plt.plot( data )
    plt.plot( dummy )
    plt.plot( resul )
    plt.plot( [th*i for i in digitalData] )
    plt.show()
    '''
    ToT = xinc*1e9* digitalData.count(1)
    ToA_CFD = times[zero_ind]

    # zero_ind, digitalData
    return ToA_CFD, ToT, th

# Plot each distribution of TOAs calculated with CFD
def plot_TT(cfdTimes, maximumVs):
    TTS_CFD       = np.std(cfdTimes)
    TTmean_CFD    = np.mean(cfdTimes)
    meanAmplitude = np.mean(maximumVs)
    if not os.path.isdir("Figures"):
        os.makedirs("Figures/TOAdistributions")
    axmin=min(cfdTimes)//0.5*0.5
    axmax=max(cfdTimes)//0.5*0.5+0.5
    fig, ax = plt.subplots()
    n, bins, patches = plt.hist(cfdTimes, 200,(axmin,axmax)) #(58.5,59.5)
    #plt.xlim(axmin,axmax)
    plt.title('Transient time, CFD at {}% fraction'.format(cfd_frac*100))
    plt.text(0.05, 0.95,'std: {:.4f} ns'.format(TTS_CFD),     transform=ax.transAxes)
    plt.text(0.05, 0.90,'mean: {:.4f} ns'.format(TTmean_CFD), transform=ax.transAxes)
    plt.text(0.05, 0.85,'X = {}mm,  Y = {}mm'.format(X,Y),    transform=ax.transAxes)
    plt.xlabel('Time [ns] ')
    plt.ylabel('Entries')
    name = "TT_CFD_{}_X{}_Y{}.png".format(cfd_frac*100,X,Y)
    plt.savefig('Figures/TOAdistributions/'+name)
    # plt.show()
    # plt.clf()
    plt.close(fig)


#---------------------------------------------------------------------------------#
#                              main                                               #
#---------------------------------------------------------------------------------#

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description=
            '''Analyzes measurements of a PMT in a grid of points
            Provide the name of the folder containing data.
            ''')
    parser.add_argument('pedRange',  type=int, nargs='?', default=200,
            help='range from 0 to calculate pedestal mean (in samples, usually of 0.2 ns)')
    parser.add_argument('cut_ini',   type=int, nargs='?', default=250,
            help='starting point of signal (in samples)')
    parser.add_argument('cut_end',   type=int, nargs='?', default=1024,
            help='ending point of signal (in samples)')
    parser.add_argument('ficheros',   type=str, nargs='+',
            help='directory were data is stored or list of data files. Files should start with P')
    args = parser.parse_args()

    pedRange = args.pedRange
    cut_ini  = args.cut_ini
    cut_end  = args.cut_end
    ficheros = args.ficheros
    print(pedRange, cut_ini, cut_end, ficheros)

    cfd_frac=0.5 # !change
    LEthr=200 # !change
    pol=-1 # !change

    # Find files if a folder name is passed
    # Only files starting with 'P' are read so only PMT signals are selected, ignoring Laser Trigger.
    # CHANGE THIS IF FILE NAMES ARE DIFFERENT !!!
    # Files sould be named with the format: PMTsignal_X13.5mm_Y-2mm.bin
    for pseudofichero in ficheros:
        if os.path.isdir(pseudofichero):
            ficheros = os.listdir(pseudofichero) #"./FirstData" # !revisar
            ficheros = [pseudofichero+'/'+str(fichero) for fichero in ficheros if fichero[0]=='P'] #"./FirstData/"
    if not os.path.exists('TTS.txt'):
        with open('TTS.txt','a') as TTS:
            TTS.write('X Y stddev mean filename CFD_threshold_fraction') # !revisar

    # loop over files
    for fichero in ficheros:
        X = re.search('_X(.*?)mm', fichero).group(1)
        Y = re.search('_Y(.*?)mm', fichero).group(1)
        print("X: {} mm,  Y: {} mm ".format(X,Y))
        print( "Processing file %s" % fichero)
        fd = open( fichero, "rb" )
        file_size = os.path.getsize( fichero )
        pedestal = []
        charges = []
        maximumVs = []
        maximumTimes = []
        cfdTimes = []
        leTimes = []
        ToA_CFDs = []
        ToTs = []
        ths = []

        # loop current file
        while file_size > 0:
            try:
                header, waveform, wave_size = read_waveform( fd )
                if pol==-1:
                    waveform=[pol*i for i in waveform]
                pedestal.append( calculate_pedestal( waveform, pedRange ) )
                times   = [ 1e9 * ( header[ 1 ] * value + header[ 0 ] ) for value in range( len( waveform ) ) ] # ns
                samples = [ 1e3 * value for value in waveform ]                                                 # mV
                samples_PS = np.array( samples ) - 1e3 * pedestal[-1]    # Pedestal substracted

                peak_ampl, peak_time, cfdTime, leTime = analyze_waveform(samples_PS, times, cfd_frac, LEthr)
                charge = calculate_charge( waveform, pedestal[ -1 ], header[ 1 ], cut_ini, cut_end)
                maximumVs.append(    peak_ampl   )
                maximumTimes.append( peak_time   )
                cfdTimes.append(     cfdTime     )
                leTimes.append(      leTime      )
                charges.append(      charge      )

                ToA_CFD, ToT, th    = getCFDThreshold(times, list(samples_PS), 6.25e-12, len(samples_PS), attenuation=3.0102999566, delay=1,    threshold= 0)
                ToA_CFDs.append(ToA_CFD)
                ToTs.append(ToT)
                ths.append(th)

            except:
                print('invalid event')

            file_size -= wave_size
        # end loop inside current file

        TTS_CFD       = np.std(cfdTimes)
        TTmean_CFD    = np.mean(cfdTimes)
        meanAmplitude = np.mean(maximumVs)

        # Plot TT
        plot_TT(cfdTimes, maximumVs)

        # Write results to TTS.txt file
        line = '\n {} {} {} {} {} {} {}'.format(X, Y, TTS_CFD, TTmean_CFD, fichero, cfd_frac, meanAmplitude)
        # '\n', str(X), str(Y), str(TTS_CFD), str(TTmean_CFD), str(fichero), str(cfd_frac), str(meanAmplitude)
        with open('TTS.txt','a') as TTS:
            TTS.write(line)
        fd.close()

    # end loop over files
