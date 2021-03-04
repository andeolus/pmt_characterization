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

# a2 = [6] #  !change
# a3 = [-9]
a2 =  [-15+2*i for i in range(13)] # !change
a3 =  [-13+2*i for i in range(13)]# !change

num_waveforms = 4 # !change 1000

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

        dataFolder='NO_PMT_prova' # !change
        if not os.path.isdir(dataFolder):
            os.mkdir(dataFolder)
        waveformFile1 = open(dataFolder+"/PMTsignal" + "_X" + str( ax2 ) + "mm_Y" + str( ax3 ) + "mm.bin","wb")
        waveformFile4 = open(dataFolder+"/LaserTrigger" + "_X" + str( ax2 ) + "mm_Y" + str( ax3 ) + "mm.bin","wb")
        for i in range(num_waveforms):
            scope.single()
            waveform1 = scope.data_waveform("ch1") # !change
            waveform4 = scope.data_waveform("ch4") # !change
            waveformFile1.write(waveform1) # !change
            waveformFile4.write(waveform4) # !change
        waveformFile1.close() # !change
        waveformFile4.close() # !change
