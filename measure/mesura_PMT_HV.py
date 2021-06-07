# -*- coding: utf-8 -*-

import time
import os
import numpy as np
import sys
import argparse
from OOFlex.interface.InterfaceFactory import InterfaceFactory
from OOFlex.measurement.Measure import Measure
from OOFlex.csvfiles.CSVWriter import CSVWriter

print "python {}".format(sys.argv[0])

parser = argparse.ArgumentParser(
    description=
    '''Make measurements of n waveforms. Provide the Voltage of each measure.
    Provide the name of the folder where you want data to be saved.
    '''
    )
parser.add_argument('HV', type=float, nargs='?', default=0,
    help='Voltage')
parser.add_argument('name', type=str,   nargs='?', default="proves",
    help='''name of the folder where you want data to be saved.
            "new" for automatic format data_HV_{date}''')
parser.add_argument('num_waveforms', type=int,   nargs='?', default=1000,
    help='number of waveforms to take at each point')
parser.add_argument('PMT_ch', type=int, nargs='?', default=1,
    help='PMT channel in the oscilloscope')
parser.add_argument('LASER_ch', type=int, nargs='?', default=4,
    help='Laser channel in the oscilloscope')
args = parser.parse_args()

voltage = args.HV
num_waveforms = args.num_waveforms
PMT_channel = 'ch{n}'.format(n=args.PMT_ch)
LASER_channel = 'ch{n}'.format(n=args.LASER_ch)
dataFolder = args.name
if (dataFolder=="new"):
    date=time.strftime("%Y_%m_%d_%H%M")
    dataFolder='data_HV_{date}'.format(date=date) # !change
if not os.path.isdir(dataFolder):
    os.mkdir(dataFolder)

ax1=0
ax2=0

factory = InterfaceFactory( "setup.ini" )
time.sleep( 0.3 )
ESP300 = factory.getDevice( "motionController" )
scope = factory.getDevice( "scope" )
time.sleep( 0.3 )

wf_PMT_name   = "{dataFolder}/PMTsignal_X{ax1}mm_Y{ax2}mm_Voltage_{voltage}.bin".format(
    dataFolder=dataFolder,ax1=ax1,ax2=ax2,voltage=voltage)
wf_LASER_name = "{dataFolder}/LaserTrigger_X{ax1}mm_Y{ax2}mm_Voltage_{voltage}.bin".format(
    dataFolder=dataFolder,ax1=ax1,ax2=ax2,voltage=voltage)
waveformFile_PMT   = open(wf_PMT_name,"wb")
waveformFile_LASER = open(wf_LASER_name,"wb")

for i in range(num_waveforms):
    scope.single()
    waveform_PMT   = scope.data_waveform(PMT_channel)
    waveform_LASER = scope.data_waveform(LASER_channel)
    waveformFile_PMT.write(waveform_PMT)
    waveformFile_LASER.write(waveform_LASER)
waveformFile1.close()
waveformFile4.close()
