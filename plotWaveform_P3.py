# -*- coding: utf-8 -*-

import pylab
import sys
import struct
import os.path
import getopt
import numpy as np
from scipy import optimize
from matplotlib.ticker import MultipleLocator
from itertools import cycle


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

def plot_parameters2():
  pylab.rcParams[ 'lines.linewidth' ] = 2
  pylab.rcParams[ 'lines.markeredgewidth' ] = 2
  pylab.rcParams[ 'lines.markersize' ] = 20
  pylab.rcParams[ 'font.size' ] = 23
  pylab.rcParams[ 'font.weight' ] = 'semibold'
  pylab.rcParams[ 'axes.linewidth' ] = 2
  pylab.rcParams[ 'axes.titlesize' ] = 20
  pylab.rcParams[ 'axes.labelsize' ] = 25
  pylab.rcParams[ 'axes.labelweight' ] = 'semibold'
  pylab.rcParams[ 'ytick.major.pad' ] = 15
  pylab.rcParams[ 'xtick.major.pad' ] = 15
  pylab.rcParams[ 'legend.fontsize' ] = 20
  pylab.rcParams[ 'grid.linewidth' ] = 1.5


def read_waveform( fd ):
  # Ponemos "h" o "H" en el unpack dependiendo de si usamos el MSO9404 o el MSOX3034A respectivamente
  #Asi como el wave_size con 40 o 36 siguiendo lo mismo de arriba
  header = struct.unpack( 4 * 'd' , fd.read( 4 * 8 ) )
  datatype = 'h'
  print( "Header:", header)
  waveform_length = struct.unpack( 1 * 'i' , fd.read( 1 * 4 ) )[ 0 ]
  waveform = [ value * header[ 3 ] + header[ 2 ] for value in struct.unpack( int( waveform_length/2 ) * datatype, fd.read( waveform_length  ) ) ]
  wave_size = struct.calcsize(4*'d' + 'i' + waveform_length*datatype) # 40 + waveform_length*2
  print( "Waveform length:", len( waveform ) )
  return header, waveform, wave_size


def mode( data, mini = None, maxi = None, bins=100):
  if bins == 1:
    return (maxi + mini)/2
  if mini == None:
    mini = min(data)
  if maxi == None:
    maxi = max(data)
  #A list of the bin each value should be counted
  hist = [ int(bins*(d-mini)/(maxi-mini)) for d in data if d >= mini and d <= maxi ]
  hist = [ hist.count(i) for i in range(bins+1) ]
  hist[-2] += hist[-1]
  hist = hist[:-1]
  if len([ i for i,d in enumerate(hist) if d == max(hist) ]) > 1:
    return mode(data, mini, maxi, bins-1)
  else:
    return mini + (0.5+hist.index(max(hist)))*(maxi-mini)/bins


def calculate_pedestal( waveform, pedRange ):
  "Remove the hash key to visualize the piece of waveform used to calculate the pedestal."
  pylab.plot( range( pedRange ), waveform[ : pedRange ] )
  pylab.ylabel( "Pedestal" )
  pylab.grid( True )
  return np.average( waveform[ : pedRange ] )



def calculate_charge( waveform, pedestal, xinc, cut_ini, cut_end ):
  "Remove the hash key to visualize the piece of waveform used to calculate the charge of the waveform."

#  charge = 0
  wave_ped_subs = np.array( waveform ) - pedestal
#  for it in range( cut_ini, cut_end - 1 ):
#    charge += ( wave_ped_subs[ it ] + ( wave_ped_subs[ it + 1 ] - wave_ped_subs[ it ] ) / 2 ) * xinc / 1250  #Este 1250 es la resistencia corregida
  pylab.plot( cut_ini+np.array( range( cut_end-cut_ini ) ), wave_ped_subs[ cut_ini : cut_end ] )
  pylab.ylabel( "Signal" )
  pylab.grid( True )
  return charge


def plot_waveform( header, ax, waveform, pedestal ):
  pylab.minorticks_on()
  ax.xaxis.set_minor_locator( MultipleLocator( 10 ) )
  ax.yaxis.set_minor_locator( MultipleLocator( 5 ) )
  times =  [ 1e9 * ( header[ 1 ] * value + header[ 0 ] ) for value in range( len( waveform ) ) ]
  voltages = [ 1e3 * value for value in waveform ]
  pylab.plot( times, voltages, "-", label = "waveform" )
  pylab.plot( times, np.array( voltages ) - 1e3 * pedestal, "-", label="pedestal substracted" )
  pylab.xlim( [ min( times ), max( times ) ] )
  pylab.xlabel( "Time (ns)" )
  pylab.ylabel( "Voltage (mV)" )
  pylab.grid( True, which = 'major', linestyle = '--')
  pylab.grid( True, which = 'minor', linestyle = ':')
  pylab.grid( True, which = 'both' )
  pylab.legend()
  pylab.tight_layout()


def AverageFilter( waveform, N ):
  AvWaveformRe = np.copy(waveform)
  AvWaveformRe[N] = sum(waveform[:2*N+1])/(2*N+1)

  for it in range(N+1, len(waveform)-N):
    AvWaveformRe[it] = AvWaveformRe[it-1] + (waveform[it + N] - waveform[it - N - 1])/(2*N+1)
  ax = pylab.subplot( 212 )
  pylab.plot( AvWaveformRe )
  pylab.ylabel( "Recursive Average with " + str(N) + " points")
  pylab.grid( True )
  pylab.show()

#---------------------------------------------------------------
#---------------------------------------------------------------
#---------------------------------------------------------------


if __name__ == "__main__":
  pedRange, cut_ini, cut_end, ficheros, NumPoints = getparams( sys.argv[ 1: ] )
  for fichero in ficheros:
    print( "Processing file %s" % fichero)
    fd = open( fichero, "rb" )
    file_size = os.path.getsize( fichero )
    pedestal = []
    charge = []
    #pedRange = 300
    #cut_ini = 350
    #cut_end = 450
    #NumPoints = 0
    while file_size > 0:
      plot_parameters2()
      fig = pylab.figure( 1 )
      ax = pylab.subplot( 212 )
      try:
        header, waveform, wave_size = read_waveform( fd )

        pedestal.append( calculate_pedestal( waveform, pedRange ) )
        ax = pylab.subplot( 211 )
        plot_waveform( header, ax, waveform, pedestal[ -1 ] )   #Remove the hash key to visualize the waveforms
        plot_parameters2()
        fig = pylab.figure( 2 )
        ax = pylab.subplot( 211 )
        charge = calculate_charge( waveform, pedestal[ -1 ], header[ 1 ], cut_ini,  cut_end)
        AverageFilter( waveform, NumPoints )
        file_size -= wave_size
      except( ValueError):
        print( "error" )
        continue
      pylab.show()
  fd.close()
