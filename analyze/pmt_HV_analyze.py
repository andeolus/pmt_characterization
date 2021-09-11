# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import sys
import struct
import os.path
import argparse
import numpy as np
import re
import os


def read_waveform( fd ):
  # Ponemos "h" o "H" en el unpack dependiendo de si usamos el MSO9404 o el MSOX3034A respectivamente
  #Asi como el wave_size con 40 o 36 siguiendo lo mismo de arriba
  header = struct.unpack( 4 * 'd' , fd.read( 4 * 8 ) )
  datatype = 'h'
  # print( "Header:", header)
  waveform_length = struct.unpack( 1 * 'i' , fd.read( 1 * 4 ) )[ 0 ]
  waveform = [ value * header[ 3 ] + header[ 2 ] for value in struct.unpack( int( waveform_length/2 ) * datatype, fd.read( waveform_length  ) ) ]
  wave_size = struct.calcsize(4*'d' + 'i' + waveform_length*datatype) # 40 + waveform_length*2
  # print( "Waveform length:", len( waveform ) )
  return header, waveform, wave_size


def calculate_pedestal( waveform, pedRange ):
  "Remove the hash key to visualize the piece of waveform used to calculate the pedestal."
  # pylab.plot( range( pedRange ), waveform[ : pedRange ] )
  # pylab.ylabel( "Pedestal" )
  # pylab.grid( True )
  return np.average( waveform[ : pedRange ] )

# Charge without pedestal
def calculate_charge( waveform, pedestal, xinc, cut_ini, cut_end ):
  "Remove the hash key to visualize the piece of waveform used to calculate the charge of the waveform."
  charge = 0
  wave_ped_subs = np.array( waveform ) - pedestal
  for it in range( cut_ini, cut_end - 1 ):
    charge += ( wave_ped_subs[ it ] + ( wave_ped_subs[ it + 1 ] - wave_ped_subs[ it ] ) / 2 ) * xinc / 50  #Este 1250 es la resistencia corregida
  return charge

# Charge with pedestal
def calculate_charge_wp( waveform, pedestal, xinc, cut_ini, cut_end ):
  "Remove the hash key to visualize the piece of waveform used to calculate the charge of the waveform."
  charge = 0
  wave = np.array( waveform )
  for it in range( cut_ini, cut_end - 1 ):
    charge += ( wave[ it ] + ( wave[ it + 1 ] - wave[ it ] ) / 2 ) * xinc / 50  #Este 1250 es la resistencia corregida
  return charge

# "Mathematical" CFD, takes the closest value to f% of the total amplitude
def analyze_waveform(voltagesPS, times, f, thr):
  maximumV = max(voltagesPS)
  maxVIndex = np.argmax(voltagesPS)
  maximumTime = times[maxVIndex]
  fracIndex = (np.abs(voltagesPS[:maxVIndex]-f*maximumV)).argmin()
  cfdTime = times[fracIndex]

  leIndex = (np.abs(voltagesPS[:maxVIndex]-thr)).argmin()
  m,b = np.polyfit(times[leIndex-5:leIndex+5],voltagesPS[leIndex-5:leIndex+5],1)
  leTime= (thr-b)/m
  # leTime_nointer = times[leIndex] # Leading edge time, no interpolation.
  return  maximumV, maximumTime, cfdTime, leTime


# Electronically simulated CFD
def getCFDThreshold( times, waveform, xinc, points, attenuation=0, delay=0, threshold=0 ):
    ''' attenuation : db
        delay       : ns
        threshold   : V (minimum value)
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
    max_ind  = waveform.index(max(waveform))
    zero_ind = 0
    for i in range(max_ind)[::-1]:
      if resul[i] <= 0:
        zero_ind = i
        break

    #Calculate the threshold
    try:
      th = waveform[zero_ind] + (waveform[zero_ind+1] - waveform[zero_ind])*(0 - resul[zero_ind])/(resul[zero_ind+1] - resul[zero_ind])
      digitalData      = list( np.int8(np.array(waveform) >= th) )
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


#----------------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=
        '''Analyzes measurements of a PMT in a grid of points
        Provide the name of the folder containing data.
        ''')
    parser.add_argument('-r','--pedRange',  type=int, nargs='?', default=200,
        help='range from 0 to calculate pedestal mean (in samples, usually of 0.2 ns)')
    parser.add_argument('-i','--cut_ini',   type=int, nargs='?', default=250,
        help='starting point of signal (in samples)')
    parser.add_argument('-e','--cut_end',   type=int, nargs='?', default=1024,
        help='ending point of signal (in samples)')
    parser.add_argument('ficheros',   type=str, nargs='+',
        help='directory were data is stored or list of data files. Files should start with P')
    args = parser.parse_args()
    pedRange = args.pedRange
    cut_ini  = args.cut_ini
    cut_end  = args.cut_end
    ficheros = args.ficheros
    print(pedRange, cut_ini, cut_end, ficheros)
    cfd_frac=0.5
    LEthr=200

    # Find files if a folder name is passed
    # Only files starting with 'P' are read so only PMT signals are selected, ignoring Laser Trigger. CHANGE THIS IF FILE NAMES ARE DIFFERENT !!!
    # Files sould be named with the format PMTsignal_X13.5mm_Y-2mm.bin
    for pseudofichero in ficheros:
        if os.path.isdir(pseudofichero):
            ficheros = os.listdir(pseudofichero) #"./FirstData"
            ficheros = [pseudofichero+'/'+str(fichero) for fichero in ficheros if fichero[0]=='P'] #"./FirstData/"

    if not os.path.exists('TTS.txt'):
        with open('TTS.txt','a') as TTS:
            TTS.write('X Y stddev mean filename CFD_threshold_fraction maxVmean HV Gain Gain2 nphe nphe2')

    for fichero in ficheros:
        X = 0 #re.search('_X(.*?)mm', fichero).group(1)
        Y = 0 #re.search('_Y(.*?)mm', fichero).group(1)
        print("X,  "+ str(X) + '  Y, '+str(Y))
        print( "Processing file %s" % fichero)
        fd = open( fichero, "rb" )
        file_size = os.path.getsize( fichero )
        pedestal = []
        charges = []
        chargeswp = []
        chargesp = []
        maximumVs = []
        maximumTimes = []
        cfdTimes = []
        leTimes = []
        leTimesCl = [ [],[],[] ]
        ToA_CFDs = []
        ToTs = []
        ths = []

    while file_size > 0:
        header, waveform, wave_size = read_waveform( fd )
        pol=-1
        waveform=[pol*i for i in waveform]
        if waveform == []:
            print("this waveform contains nothing")
        else:
            pedestal.append( calculate_pedestal( waveform, pedRange ) )
            times =  [ 1e9 * ( header[ 1 ] * value + header[ 0 ] ) for value in range( len( waveform ) ) ]
            voltages = [ 1e3 * value for value in waveform ]
            voltagesPS = np.array( voltages ) - 1e3 * pedestal[-1]  #Pedestal substracted

        try:
            maximumV, maximumTime, cfdTime, leTime = analyze_waveform( voltagesPS, times, cfd_frac , LEthr)
            maximumVs.append( maximumV )
            maximumTimes.append(maximumTime)
            cfdTimes.append(cfdTime)
            leTimes.append(leTime)
            charges.append( calculate_charge( waveform, pedestal[ -1 ], header[ 1 ], cut_ini,  cut_end) )
            chargeswp.append( calculate_charge_wp( waveform, pedestal[ -1 ], header[ 1 ], cut_ini,  cut_end) )
            chargesp.append( calculate_charge_wp( waveform, pedestal[ -1 ], header[ 1 ], 0,  cut_end-cut_ini) )
              # leTimesClassifier(voltagesPS, times, 100,leTimesCl)

            ToA_CFD, ToT, th  = getCFDThreshold(times, list(voltagesPS), 6.25e-12, len(voltagesPS), attenuation=3.0102999566, delay=1,  threshold= 0)
            ToA_CFDs.append(ToA_CFD)
            ToTs.append(ToT)
            ths.append(th)
        except:
            print("his waveform has a strange shape probably")
        file_size -= wave_size

    fracTs_jitter= np.std(cfdTimes)
    fracTs_mean= np.mean(cfdTimes)
    meanAmplitude=np.mean(maximumVs)

    HV = re.search('Voltage(.*?).bin', fichero).group(1)
    nphe= ((np.mean(charges))**2) / ((np.std(charges))**2)
    nphe2= (np.mean(chargeswp)-np.mean(chargesp))**2 / ((np.std(chargeswp))**2-(np.std(chargesp))**2)
    gain= np.std(charges)**2/np.mean(charges)/1.60217662e-19
    gain2= (np.std(chargeswp)**2-np.std(chargesp)**2) /np.mean(charges) /1.60217662e-19
    print(np.std(charges)**2/np.mean(charges)/1.60217662e-19)
    print('means: ',np.mean(charges),np.mean(chargeswp)-np.mean(chargesp),np.mean(chargesp),np.mean(chargeswp))
    print('devs: ',np.std(charges), (np.std(chargeswp)**2-np.std(chargesp)**2)**0.5, np.std(chargesp), np.std(chargeswp))

    # Write results to TTS.txt file
    with open('TTS.txt','a') as TTS:
        results='\n{X} {Y} {fracTs_jitter} {fracTs_mean} {fichero} {cfd_frac} {meanAmplitude} {HV} {gain} {gain2} {nphe} {nphe2}'.format(
        X=X,Y=Y,fracTs_jitter=fracTs_jitter,fracTs_mean=fracTs_mean,fichero=fichero,
        cfd_frac=cfd_frac,meanAmplitude=meanAmplitude,HV=HV,gain=gain,gain2=gain2,nphe=nphe,nphe2=nphe2)
        TTS.write(results)
    fd.close()


    # Charges without pedestal
    fig, ax = plt.subplots()
    n, bins, patches = plt.hist(charges)
    plt.title('Charges without pedestal')
    plt.text(0.05, 0.95,'std: {:.4g} C'.format(np.std(charges)), transform=ax.transAxes)
    plt.text(0.05, 0.90,'mean: {:.4g} C'.format(np.mean(charges)), transform=ax.transAxes)
    plt.text(0.05, 0.85,'HV= '+str(HV)+ 'V', transform=ax.transAxes)
    plt.xlabel(' Charge [C] ')
    plt.ylabel('Counts')
    name='Charges_'+str(HV)+'.png'
    plt.savefig('Figures/Charges/'+name)
    # plt.show()
    # plt.clf()
    plt.close(fig)

    # Charges with pedestal
    fig, ax = plt.subplots()
    n, bins, patches = plt.hist(chargeswp)
    plt.title('Charges with pedestal')
    plt.text(0.05, 0.95,'std: {:.4g} C'.format(np.std(chargeswp)), transform=ax.transAxes)
    plt.text(0.05, 0.90,'mean: {:.4g} C'.format(np.mean(chargeswp)), transform=ax.transAxes)
    plt.text(0.05, 0.85,'HV= '+str(HV)+ 'V', transform=ax.transAxes)
    plt.xlabel(' Charge [C] ')
    plt.ylabel('Counts')
    name='Chargeswp_'+str(HV)+'.png'
    plt.savefig('Figures/Charges/'+name)
    # plt.show()
    # plt.clf()
    plt.close(fig)

    #  Charges of the pedestal
    fig, ax = plt.subplots()
    n, bins, patches = plt.hist(chargesp)
    plt.title('Charges of the pedestal')
    plt.text(0.05, 0.95,'std: {:.4g} C'.format(np.std(chargesp)), transform=ax.transAxes)
    plt.text(0.05, 0.90,'mean: {:.4g} C'.format(np.mean(chargesp)), transform=ax.transAxes)
    plt.text(0.05, 0.85,'HV= '+str(HV)+ 'V', transform=ax.transAxes)
    plt.xlabel(' Charge [C] ')
    plt.ylabel('Counts')
    name='Chargesp_'+str(HV)+'.png'
    plt.savefig('Figures/Charges/'+name)
    # plt.show()
    # plt.clf()
    plt.close(fig)
