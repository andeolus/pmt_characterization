# -*- coding: utf-8 -*-
from __future__ import print_function
import argparse
import time
import os
import numpy as np
import sys
from OOFlex.interface.InterfaceFactory import InterfaceFactory
from OOFlex.measurement.Measure import Measure
from OOFlex.csvfiles.CSVWriter import CSVWriter

print( "python {} xmin xmax xN ymin ymax yN --bool_wait ".format(sys.argv[0]) )

def scroll(xmin, xmax, xN, ymin, ymax, yN, bool_wait):
    """Scroll scanning a grid of xN*yN points
        between xmin, xmax and ymin, ymax.
    """
    factory = InterfaceFactory( "setup.ini" )
    time.sleep( 0.3 )
    ESP300 = factory.getDevice( "motionController" )
    time.sleep( 0.3 )

    # choose min, max, N: force step
    xstep = float(xmax-xmin)/float(xN-1) if xN!=1 else 0
    ystep = float(ymax-ymin)/float(yN-1) if yN!=1 else 0
    a2 = [ xmin + xstep*i for i in range( xN )]
    a3 = [ ymin + ystep*i for i in range( yN )]

    print(a2)
    print(a3)

    for ax2 in a2:
        for ax3 in a3:
            print("moving to {} {} ".format(ax2,ax3))
            if bool_wait:
                if sys.version_info[0] == 2: raw_input("moving to {} {} Press Enter to continue... ".format(ax2,ax3))
                if sys.version_info[0] == 3: input("moving to {} {} Press Enter to continue... ".format(ax2,ax3))
            else:
                time.sleep( 0.3 )
            try:
                print( "aiming to: ", ax2, ax3 )
                ESP300.setA(ax2,2)
                time.sleep( 1 )
                ESP300.setA(ax3,3)
                time.sleep( 2 ) #1
                x= float(ESP300.tpA(2))
                time.sleep( 1 )
                y=float(ESP300.tpA(3))
                print( "X, Y:    ", x , y )
                # print( "Y: ", y )
                if (abs(ax2-x)>0.1 or abs(ax3-y)>0.1):
                    print( " discrepant! Trying again:" )
                    ESP300.setA2(ax2)
                    ESP300.setA3(ax3)
                    time.sleep( 1 )
                    x= float(ESP300.tpA2())
                    y=float(ESP300.tpA3())
                    print( "X: ", float(ESP300.tpA2()) )
                    print( "Y: ", float(ESP300.tpA3()) )
                print( "-------------" )
            except:
                print( "ERROR!!!" )
                print( "Trying again..." )
                print( "aiming to: ", ax2, ax3 )
                ESP300.setA(ax2,2)
                ESP300.setA(ax3,3)
                time.sleep( 4 ) #1
                x= float(ESP300.tpA(2))
                y=float(ESP300.tpA(3))
                print( "X, Y:    ", x , y )
                # print( "Y: ", y )
                if (abs(ax2-x)>0.1 or abs(ax3-y)>0.1):
                    print( " discrepant! Trying again:" )
                    ESP300.setA2(ax2)
                    ESP300.setA3(ax3)
                    time.sleep( 1 )
                    x= float(ESP300.tpA2())
                    y=float(ESP300.tpA3())
                    print( "X: ", float(ESP300.tpA2()) )
                    print( "Y: ", float(ESP300.tpA3()) )
                print( "-------------" )


if __name__=="__main__":
    parser = argparse.ArgumentParser(
            description=
            '''Scroll scanning a grid of xN*yN points
            between xmin, xmax and ymin, ymax.
            '''
            )
    parser.add_argument('xmin', type=float, nargs='?', default=0,  help='starting point in x axis')
    parser.add_argument('xmax', type=float, nargs='?', default=10, help='ending point in x axis')
    parser.add_argument('xN',   type=int,   nargs='?', default=11, help='number of point in x axis')
    parser.add_argument('ymin', type=float, nargs='?', default=0,  help='starting point in y axis')
    parser.add_argument('ymax', type=float, nargs='?', default=10, help='ending point in y axis')
    parser.add_argument('yN',   type=int,   nargs='?', default=11, help='number of point in y axis')
    parser.add_argument('--bool_wait',     default=0, action='store_true',
            help='wait for user keyboard stroke before moving to next point') # type=bool,  nargs='?',
    args = parser.parse_args()

    scroll( args.xmin, args.xmax, args.xN, args.ymin, args.ymax, args.yN, args.bool_wait)
