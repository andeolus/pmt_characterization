
import re
import os

files=os.listdir()

PMT='PMT' #'TS0340_tappered' ; 'ZF0002_tappered'

HV=input('please enter the HV parameter value: ')
for f in files:
  if f=='data-ch1-0.bin':
    os.rename(f,'LaserTrigger_'+PMT+'_X0mm_Y0mm_Voltage'+str(HV)+'.bin')
  if f=='data-ch2-0.bin':
    os.rename(f,'PMT_'+PMT+'_X0mm_Y0mm_Voltage'+str(HV)+'.bin')


# oldPMTname='SecondSocket' # 'TS0340_SecondSocket'
# newPMTname='tappered'
# # bad PMT naming
# for f in files:
#     if oldPMTname in f:
#         os.rename(f,re.sub(oldPMTname,newPMTname,f))
