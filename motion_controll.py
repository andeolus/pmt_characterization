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

A1 = sys.argv[1]
A2 = sys.argv[2]
A3 = sys.argv[3]

ESP300.setA1(A1)
time.sleep( 0.3 )
ESP300.setA2(A2)
time.sleep( 0.3 )
ESP300.setA3(A3)
