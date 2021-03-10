# -*- coding: utf-8 -*-

import socket
import sys
import os
import time
import gzip
import pylab
import numpy as np
import struct


"""
Waveform acquisition.
Each file contains 1k of waveforms.
Data format: 4*DOUBLE(8BYTES)+1*INTEGER(4BYTES)+(N/2)*SHORT(2BYTES)
  4*DOUBLE: xor, xinc, yor, yinc
  1*INTEGER: Number of bytes will follow for the message
  (N/2)*SHORT: Message where N=previous value
"""


def openSocket():
  #ip_address = "10.0.0.1" #MSO9404A
  ip_address = "192.168.1.133" #MSO9404A
  port = 5025 #MSO9404A
  sck = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
  sck.connect( ( ip_address, port ) )
  sck.send( "*IDN?\n" )
  idn = sck.recv( 1024 )
  print "Osc id = %s" % idn
  return sck


def open_files( channels ):
  files = {}
  for chan in channels:
    files[ chan ] = open( "data-" + chan + ".bin", "wb" )
  return files


def close_files( files ):
  for key in files.keys():
    files[ key ].close()


def acq_conf( sock ):
  sock.send( ":ACQUIRE:COMPLETE 100\n" )
  sock.send( ":SYSTem:HEADer OFF\n" )
  sock.send( ":WAVeform:STReaming 0\n" )
  sock.send( ":WAVeform:FORMat WORD\n" )
  sock.send( ":WAVeform:BYTeorder LSBFirst\n" )
  #sock.send( ":ACQuire:POINts:ANALog 4000\n" )  #Esto hay que entenderlo!!!!!


def read_until_match( sock, eop ):
  buf = ""
  while True:
    buf += sock.recv( 1024 )
    found = buf.find( eop )
    if found > -1:
      return buf[:found]


def read_data_points_ascii( sock ):
  buf = sock.recv( 10 )
  while buf.find( "\n" ) == -1:
    buf += sock.recv( 8192 )
  return [float(f) for f in buf[:-1].split(",") if f ]


def read_data_points( sock ):
  buf = sock.recv( 10 )
  assert buf[ 0 ] == "#"
  sl = int( buf[ 1 ] )
  l = int( buf[ 2 : 2 + sl ] )
  buf = buf[ 2 + sl : ]
#  print l
  while len( buf ) <= l:
#    print "LOOP", len( buf )
    buf += sock.recv( l + 1 - len( buf ) )
#  print "OUT", len( buf ), "[%s]" % buf[ -1 ]
  assert buf[ -1 ] == '\n'
  return buf [ :-1 ]


def get_fields_from_preamble( preamble ):
  fields = preamble.split( "," )
  points = int( float( fields[ 2 ] ) )
  xinc = float( fields[ 4 ] )
  xor = float( fields[ 5 ] )
  yinc = float( fields[ 7 ] )
  yor = float( fields[ 8 ] )
  return fields, points, yinc, yor, xinc, xor


def verification(sock, chan, flag):
  sock.send( ":WAVeform:VIEW MAIN\n" )
  if "ch" in chan:
    print "READING WAVEFORM IN CHANNEL %s" % chan[ -1 ]
    sock.send( ":WAVeform:SOURce CHANnel" + chan[ -1 ] + "\n" )
  elif "fn" in chan:
    print "READING WAVEFORM IN FUNCTION %s" % chan[ -1 ]
    sock.send( ":WAVeform:SOURce FUNCtion" + chan[ -1 ] + "\n" )
  sock.send( ":WAVeform:PREamble?\n" )
  preamble = read_until_match( sock, '\n' )
#  print "PREAMBLE OF THE WAVEFORM: <format>, <type>, <points>, <count> , <X increment>, <X origin>, < X reference>, <Y increment>, <Y origin>, <Y reference>, <coupling>, <X display range>, <X display origin>, <Y display range>, <Y display origin>, <date>, <time>, <frame model #>, <acquisition mode>, <completion>, <X units>, <Y units>, <max bandwidth limit>, <min bandwidth limit>"
#  print "PREAMBLE DATA %s" % preamble.split( "," )
  fields, points, yinc, yor, xinc, xor = get_fields_from_preamble( preamble )
  sock.send( ":WAVEFORM:DATA?\n" )

  data = read_data_points( sock )
  if data != '':
    flag = True
  else:
    flag = False
  len1 = len( data )
  a = str( struct.pack( 'i' , len( data ) ) )
  data = str( struct.pack( 4 * 'd' , xor, xinc, yor, yinc ) ) + str( struct.pack( 'i' , len( data ) ) ) + data
  return flag, data

def write_waveform( data, fd ):

  fd.write( data )
  fd.flush()
  return fd


#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------


if __name__ == "__main__":
  print "-----------------------------------------------------------------------"
  print "  Usage: python MSO9404A_waveform.py numWaveForms [cte = 0] [ch1, ch2, fn1 ...]  "
  print "-----------------------------------------------------------------------"
  cte = 0
  lenght_file = 5000
  if len( sys.argv ) < 3:
    exit( 1 )
  num_waveforms = int( sys.argv[ 1 ] )
  try:
    cte = int(sys.argv[2])
    del sys.argv[2]
  except:
    pass
  channels = sys.argv[ 2 : ]
  files = open_files( channels )
  sock = openSocket()
  sock.send( ":RUN\n" )
  acq_conf( sock )
  for i in range( num_waveforms ):
    if i % lenght_file == 0 and i != 0:
      it = i / lenght_file
      close_files( files )
      for chan in channels:
        print ""
        print "*********************************************************************************************"
        print "*************************   CLOSING FILE: data-%s-%s.bin   *********************************" %( chan, str( it + cte ) )
        print "*********************************************************************************************"
        os.rename( "data-" + chan + ".bin", "data-" + chan + "-%s.bin" %str( it + cte ) )
      files = open_files( channels )
    print "\nREADING WAVEFORM Num. %d" % i
    if len(channels) > 0 : sock.send( ":SINGle\n" )
    for chan in channels:
      flag = False
      while flag == False:
        flag, data = verification(sock, chan, flag)
      files[ chan ] = write_waveform( data, files[ chan ])
  close_files( files )
  for chan in channels:
    os.rename( "data-" + chan + ".bin", "data-" + chan + "-%s.bin" %str( num_waveforms/lenght_file + cte ) )
#  pylab.show()
