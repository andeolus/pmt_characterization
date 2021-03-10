# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import sys
import struct
import os.path
import getopt
import numpy as np
import re


def usage(errorCode=0):
  print( "-------------------------------------------------")
  print( "  Usage: python plotWaveform <-r [pedestal range]> <-i [signal init]> <-e [signal end]> <-n [number of points]> <-h [help]> data_files ")
  print( "-------------------------------------------------")
  sys.exit(errorCode)

def getparams(argv):
  ''' Get options from command line
      Returns
  '''

  try:
    obligatories = list('')
    opts, args = getopt.getopt(argv, 'hr:i:e:n:')

    # Default values
    pedRange = 200
    cut_ini  = 250
    cut_end  = 1024
    ficheros = []
    numPoints= 0

    # Default values
    for opt, val in opts:
      if opt[1] in obligatories: obligatories.remove(opt[1])
      if opt == '-r':
        pedRange = int(val)
      elif opt == '-i':
        cut_ini = int(val)
      elif opt == '-e':
        cut_end = int(val)
      elif opt == '-n':
        numPoints = int(val)
      elif opt == '-h':
        usage()

    if len(obligatories) > 0:
      raise

    ficheros = list(args)

  except( Exception,x):
    usage(1)

  return [pedRange, cut_ini, cut_end, ficheros, numPoints]


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


def calculate_charge( waveform, pedestal, xinc, cut_ini, cut_end ):
  "Remove the hash key to visualize the piece of waveform used to calculate the charge of the waveform."
  charge = 0
  wave_ped_subs = np.array( waveform ) - pedestal
  for it in range( cut_ini, cut_end - 1 ):
    charge += ( wave_ped_subs[ it ] + ( wave_ped_subs[ it + 1 ] - wave_ped_subs[ it ] ) / 2 ) * xinc / 1250  #Este 1250 es la resistencia corregida

  return charge


def analyze_waveform(voltagesPS, times, f, thr):
  maximumV = max(voltagesPS)
  maxVIndex = np.argmax(voltagesPS)
  maximumTime = times[maxVIndex]
  fracIndex = (np.abs(voltagesPS[:maxVIndex]-f*maximumV)).argmin()
  fracTime = times[fracIndex]

  thrIndex = (np.abs(voltagesPS[:maxVIndex]-thr)).argmin()
  m,b = np.polyfit(times[thrIndex-5:thrIndex+5],voltagesPS[thrIndex-5:thrIndex+5],1)
  thrTime= (thr-b)/m
  # PreFixthrTime = times[thrIndex]
  return  maximumV, maximumTime, fracTime, thrTime



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




# def thrTimesClassifier(voltagesPS, times, thr,thrTimesCl):
#   maximumV= max(voltagesPS)
#   maxVIndex = np.argmax(voltagesPS)
#   thrIndex = (np.abs(voltagesPS[:maxVIndex]-thr)).argmin()
#   thrTime = times[thrIndex]
#   if maximumV < 400 :
#     thrTimesCl[0].append(thrTime)
#   elif maximumV < 800:
#     thrTimesCl[1].append(thrTime)
#   else:
#     thrTimesCl[2].append(thrTime)
  # return thrTimesCl

#---------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------


if __name__ == "__main__":
  pedRange, cut_ini, cut_end, ficheros, NumPoints = getparams( sys.argv[ 1: ] )
  print(pedRange, cut_ini, cut_end, ficheros, NumPoints)
  # Ficheros in folder

  for fichero in ficheros:
    X = re.search('_X(.*)mm_', fichero).group(1)
    Y = re.search('_Y(.*)mm', fichero).group(1)
    print("X,  "+ str(X) + '  Y, '+str(Y))
    print( "Processing file %s" % fichero)
    fd = open( fichero, "rb" )
    file_size = os.path.getsize( fichero )
    pedestal = []
    charges = []
    maximumVs = []
    maximumTimes = []
    fracTimes = []
    thrTimes = []
    thrTimesCl = [ [],[],[] ]
    ToA_CFDs = []
    ToTs = []
    ths = []

    #pedRange = 300
    #cut_ini = 350
    #cut_end = 450
    #NumPoints = 0

    while file_size > 0:
      header, waveform, wave_size = read_waveform( fd )
      # with open('check.txt','a') as check:
        # check.write('negative polarity\n'+str(waveform)+'\n')
      pol=-1
      waveform=[pol*i for i in waveform]
      # with open('check.txt','a') as check:
      #   check.write('positive polarity\n'+str(waveform)+'\n')

      pedestal.append( calculate_pedestal( waveform, pedRange ) )
      times =  [ 1e9 * ( header[ 1 ] * value + header[ 0 ] ) for value in range( len( waveform ) ) ]
      voltages = [ 1e3 * value for value in waveform ]
      voltagesPS = np.array( voltages ) - 1e3 * pedestal[-1]  #Pedestal substracted

      maximumV, maximumTime, fracTime, thrTime = analyze_waveform( voltagesPS, times, 0.5 , 200)
      maximumVs.append( maximumV )
      maximumTimes.append(maximumTime)
      fracTimes.append(fracTime)
      thrTimes.append(thrTime)
      charges.append( calculate_charge( waveform, pedestal[ -1 ], header[ 1 ], cut_ini,  cut_end) )
      # thrTimesClassifier(voltagesPS, times, 100,thrTimesCl)

      ToA_CFD, ToT, th  = getCFDThreshold(times, list(voltagesPS), 6.25e-12, len(voltagesPS), attenuation=3.0102999566, delay=1,  threshold= 0)
      ToA_CFDs.append(ToA_CFD)
      ToTs.append(ToT)
      ths.append(th)

      file_size -= wave_size

    with open('dadesAnalitzades.txt','a') as da:
      da.write('\n'+'   En la configuracio: '+'python analyze_Waveform.py '+'-r '+str(pedRange)+' -i '+str(cut_ini)+' -e '+str(cut_end)+' '+str(fichero)+'\n')

      da.write('pedestal= ' + str(pedestal) + '\n')
      da.write('maximumVs= ' + str(maximumVs) + '\n')
      da.write('charges= ' + str(charges) + '\n')
      da.write('maximumTimes= ' + str(maximumTimes) + '\n')
      da.write('fracTimes50= ' +  str(fracTimes) + '\n')
      da.write('thrTimes100wlr= ' + str(thrTimes) + '\n' )
      da.write('thrTimesCl= ' + str(thrTimesCl) + '\n' )

      da.write('\n'+ 'attenuation = 3.0102999566' + 'dB'+'\n')
      da.write('ToA_CFDs_att= ' + str(ToA_CFDs)+ '\n')
      da.write('ToTs_att= ' + str(ToTs) +'\n')
      da.write('ths_att= ' + str(ths) +'\n')
      da.write(2*'\n')

    name='timeFractions_X'+str(X)+'_Y'+str(Y)+'.png'
    timefractions=fracTimes
    fig, ax = plt.subplots()
    n, bins, patches = plt.hist(timefractions, 200)
    fracTs_jitter= np.std(timefractions)
    fracTs_mean= np.mean(timefractions)
    plt.title('Time of 1/2 maximum voltage')
    plt.text(0.05, 0.95,'std: '+str(fracTs_jitter)+ ' ns', transform=ax.transAxes)
    plt.xlabel(' Time  [ns] ')
    plt.ylabel('Counts')
    plt.savefig(name)
    plt.show()
    plt.clf() #plt.close(fig)

    with open('TTS.txt','a') as TTS:
      TTS.write('\n'+str(X)+' '+str(Y)+ ' '+str(fracTs_jitter)+' '+str(fracTs_mean)+' '+str(fichero))


  fd.close()




# ________________________________________________________________

  # with open('dadesAnalitzades.txt','a') as da:
  #   da.write('\n'+'   En la configuracio: '+'python analyze_Waveform.py '+'-r '+str(pedRange)+' -i '+str(cut_ini)+' -e '+str(cut_end)+' '+str(fichero)+'\n')
  #
  #   da.write('pedestal= ' + str(pedestal) + '\n')
  #   da.write('maximumVs= ' + str(maximumVs) + '\n')
  #   da.write('charges= ' + str(charges) + '\n')
  #   da.write('maximumTimes= ' + str(maximumTimes) + '\n')
  #   da.write('fracTimes50= ' +  str(fracTimes) + '\n')
  #   da.write('thrTimes100wlr= ' + str(thrTimes) + '\n' )
  #   da.write('thrTimesCl= ' + str(thrTimesCl) + '\n' )
  #
  #   da.write('\n'+ 'attenuation = 3.0102999566' + 'dB'+'\n')
  #   da.write('ToA_CFDs_att= ' + str(ToA_CFDs)+ '\n')
  #   da.write('ToTs_att= ' + str(ToTs) +'\n')
  #   da.write('ths_att= ' + str(ths) +'\n')
  #   da.write(2*'\n')
  #
  #
  # name='timeFractions_X'+str(X)+'_Y'+str(Y)+'.png'
  # timefractions=fracTimes
  # fig, ax = plt.subplots()
  # n, bins, patches = plt.hist(timefractions, 200)
  # fracTs_jitter= np.std(timefractions)
  # plt.title('Time of 1/2 maximum voltage')
  # plt.text(0.05, 0.95,'std: '+str(fracTs_jitter)+ ' ns', transform=ax.transAxes)
  # plt.xlabel(' Time  [ns] ')
  # plt.ylabel('Counts')
  # plt.savefig(name)
  # plt.show()
  #
  # with open('TTS.txt','a') as TTS:
  #     TTS.write('\n'+str(ficheros)+' X'+str(X)+' Y'+str(Y)+' t'+str(fracTs_jitter))


'''
  n, bins, patches = plt.hist(fracTimes)
  plt.show()
'''
# cd C:\Users\andeo\Documents\Master\TFMns\data_25Feb_PACTA
# python analyze_Waveform.py -r 1000 -i 1000 -e 32000 data-fn1-0.bin
# python analyze_Waveform.py -r 5000 -i 7000 -e 10000 data-fn1-0.bin
# ./FirstData/LaserTrigger_X9mm_Y2.5mm.bin
# ./FirstData/PMTsignal_X9mm_Y-2mm.bin
# ./FirstData/PMTsignal_X9mm_Y-2mm.bin ./FirstData/PMTsignal_X9mm_Y2.5mm.bin ./FirstData/PMTsignal_X9mm_Y7mm.bin
