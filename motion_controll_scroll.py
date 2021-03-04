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

time.sleep( 0.3 )

# a2 = [-40]
a3 = [0, 1, 2 ]
a2 = [5,6,7]
# a3 = [-5,-4,-3,-2,-1,0,1,2,3,4,5 ]


for ax2 in a2:
    for ax3 in a3:
        print "aiming to: ", ax2, ax3
        ESP300.setA(ax2,2)
        time.sleep( 0.3 ) #1
        ESP300.setA(ax3,3)
        time.sleep( 2 ) #1
        x= float(ESP300.tpA(2))
        time.sleep( 0.3 )
        y=float(ESP300.tpA(3))
        print "X, Y:    ", x , y
        time.sleep( 4 ) #1


# A1 = sys.argv[1]
# A2 = sys.argv[2]
# A3 = sys.argv[3]
#
# ESP300.setA1(A1)
# ESP300.setA2(A2)
# ESP300.setA3(A3)
