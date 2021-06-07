# -*- coding: utf-8 -*-

import time
import os
import numpy as np
import sys
from OOFlex.interface.InterfaceFactory import InterfaceFactory
from OOFlex.measurement.Measure import Measure
from OOFlex.csvfiles.CSVWriter import CSVWriter

print "python {} [Axis 1] [Axis 2] [Axis 3] // abs position".format(sys.argv[0])

factory = InterfaceFactory( "setup.ini" )

time.sleep( 0.3 )

ESP300 = factory.getDevice( "motionController" )
scope = factory.getDevice( "scope" )

time.sleep( 0.3 )

voltage=900 #  !change
# a2 = [6] #  !change
# a3 = [-9]
# a2 =  [round(    3+i*0.1,1) for i in range(55)] # !change
# a3 =  [round(-21.4+i*0.1,1) for i in range(55)] # !change
a2 =[ 6 ] #+i*1.5 for i in range(2)]
a3 =[-9] # [-10.5+i*1.5 for i in range(8)]
num_waveforms = 1000 # !change 1000

for ax2 in a2:
    for ax3 in a3:
        try:
            print "aiming to: ", ax2, ax3
            ESP300.setA(ax2,2)
            time.sleep( 1 )
            ESP300.setA(ax3,3)
            time.sleep( 2 ) #1
            x= float(ESP300.tpA(2))
            time.sleep( 1 )
            y=float(ESP300.tpA(3))
            print "X, Y:    ", x , y
            # print "Y: ", y
            if (abs(ax2-x)>0.1 or abs(ax3-y)>0.1):
                print " discrepant! Trying again:"
                ESP300.setA2(ax2)
                ESP300.setA3(ax3)
                time.sleep( 1 )
                x= float(ESP300.tpA2())
                y=float(ESP300.tpA3())
                print "X: ", float(ESP300.tpA2())
                print "Y: ", float(ESP300.tpA3())
            print "-------------"
        except:
            print "ERROR!!!"
            print "Trying again..."
            print "aiming to: ", ax2, ax3
            ESP300.setA(ax2,2)
            ESP300.setA(ax3,3)
            time.sleep( 4 ) #1
            x= float(ESP300.tpA(2))
            y=float(ESP300.tpA(3))
            print "X, Y:    ", x , y
            # print "Y: ", y
            if (abs(ax2-x)>0.1 or abs(ax3-y)>0.1):
                print " discrepant! Trying again:"
                ESP300.setA2(ax2)
                ESP300.setA3(ax3)
                time.sleep( 1 )
                x= float(ESP300.tpA2())
                y=float(ESP300.tpA3())
                print "X: ", float(ESP300.tpA2())
                print "Y: ", float(ESP300.tpA3())
            print "-------------"
        dataFolder='Data_14sep_TS0340_voltages' # !change
        if not os.path.isdir(dataFolder):
            os.mkdir(dataFolder)
        waveformFile1 = open(dataFolder+"/PMTsignal" + "_X" + str( ax2 ) + "mm_Y" + str( ax3 ) + "mm_Voltage_"+str(voltage)+".bin","wb")
        waveformFile4 = open(dataFolder+"/LaserTrigger" + "_X" + str( ax2 ) + "mm_Y" + str( ax3 ) + "mm_Voltage_"+str(voltage)+".bin","wb")
        for i in range(num_waveforms):
            scope.single()
            waveform1 = scope.data_waveform("ch1")
            waveform4 = scope.data_waveform("ch4")
            waveformFile1.write(waveform1)
            waveformFile4.write(waveform4)
        waveformFile1.close()
        waveformFile4.close()
