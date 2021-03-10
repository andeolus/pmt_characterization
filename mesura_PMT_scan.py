# -*- coding: utf-8 -*-
from __future__ import print_function
import argparse
import time
import os
import numpy as np
import math
import sys
from OOFlex.interface.InterfaceFactory import InterfaceFactory
from OOFlex.measurement.Measure import Measure
from OOFlex.csvfiles.CSVWriter import CSVWriter

print "python {} name num_waveforms xmin xmax xN ymin ymax yN".format(sys.argv[0])

def scan(name, num_waveforms, xmin, xmax, xN, ymin, ymax, yN):
    """ Make measurements scanning a grid of xN*yN points
        between xmin, xmax and ymin, ymax.
    """
    factory = InterfaceFactory( "setup.ini" )
    time.sleep( 0.3 )
    ESP300 = factory.getDevice( "motionController" )
    scope = factory.getDevice( "scope" )
    time.sleep( 0.3 )

    # choose min, max, N: force step
    xstep = float(xmax-xmin)/float(xN-1) if xN!=1 else 0
    a2 = [ xmin + xstep*i for i in range( xN )]
    ystep = float(ymax-ymin)/float(yN-1) if yN!=1 else 0
    a3 = [ ymin + ystep*i for i in range( yN )]

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


            dataFolder = name
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


if __name__=="__main__":
    parser = argparse.ArgumentParser(
            description=
            '''Make measurements scanning a grid of xN*yN points
            between xmin, xmax and ymin, ymax.
            Provide a name so it can generate a folder with data.
            '''
            )
    parser.add_argument('name',          type=str,   nargs='?', default="proves",
            help='name of the folder you want to create')
    parser.add_argument('num_waveforms', type=int,   nargs='?', default=1000,
            help='number of waveforms to take at each point')
    parser.add_argument('xmin', type=float, nargs='?', default=0,  help='starting point in x axis')
    parser.add_argument('xmax', type=float, nargs='?', default=10, help='ending point in x axis')
    parser.add_argument('xN',   type=int,   nargs='?', default=11, help='number of point in x axis')
    parser.add_argument('ymin', type=float, nargs='?', default=0,  help='starting point in y axis')
    parser.add_argument('ymax', type=float, nargs='?', default=10, help='ending point in y axis')
    parser.add_argument('yN',   type=int,   nargs='?', default=11, help='number of point in y axis')
    args = parser.parse_args()

    scan( args.name, args.num_waveforms, args.xmin, args.xmax, args.xN, args.ymin, args.ymax, args.yN )

    # name = args.name
    # num_waveforms = args.num_waveforms
    # xmin = args.xmin
    # xmax = args.xmax
    # xmin = args.xN
    # ymin = args.ymin
    # ymax = args.ymax
    # ymin = args.yN
    # scan( name, num_waveforms, xmin, xmax, xN, ymin, ymax, yN )
