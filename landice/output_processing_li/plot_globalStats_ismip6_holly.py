#!/usr/bin/env python
'''
Script to plot common time-series from one or more landice globalStats files.

Modified on 2022/09/25 by Holly Han
to apply to the ISMIP6 projection such that the projection runs are
corrected for the control run. 
'''

from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import numpy as np
import numpy.ma as ma
from netCDF4 import Dataset
from argparse import ArgumentParser
from optparse import OptionParser
import matplotlib.pyplot as plt

rhoi = 910.0
rhosw = 1028.

print("** Gathering information.  (Invoke with --help for more details. All arguments are optional)")
parser = OptionParser(description=__doc__)
parser.add_option("-1", dest="file1inName", help="input filename", default="globalStats.nc", metavar="FILENAME")
parser.add_option("-2", dest="file2inName", help="input filename", metavar="FILENAME")
parser.add_option("-3", dest="file3inName", help="input filename", metavar="FILENAME")
parser.add_option("-4", dest="file4inName", help="input filename", metavar="FILENAME")
parser.add_option("-5", dest="file5inName", help="input filename", metavar="FILENAME")
parser.add_option("-6", dest="file6inName", help="input filename", metavar="FILENAME")
parser.add_option("-7", dest="file7inName", help="input filename", metavar="FILENAME")
parser.add_option("-8", dest="file8inName", help="input filename", metavar="FILENAME")
parser.add_option("-u", dest="units", help="units for mass/volume: m3, kg, Gt", default="Gt", metavar="FILENAME")
parser.add_option("--ctrl", dest="correct_ctrl", help="include if want to correct projection runs for control runs",action="store_true") 
options, args = parser.parse_args()

if options.correct_ctrl:
    print('control run will be corrected')
    ctrl_std = ""
    


print("Using ice density of {} kg/m3 if required for unit conversions".format(rhoi))

# create axes to plot into
fig = plt.figure(1, figsize=(9, 11), facecolor='w')

nrow=4
ncol=2

#xtickSpacing = 20.0

if options.units == "m3":
   massUnit = "m$^3$"
   scaleVol = 1.
elif options.units == "kg":
   massUnit = "kg"
   scaleVol = 1./rhoi
elif options.units == "Gt":
   massUnit = "Gt"
   scaleVol = 1.0e12 / rhoi
else:
   sys.exit("Unknown mass/volume units")
print("Using volume/mass units of: ", massUnit)

axVol = fig.add_subplot(nrow, ncol, 1)
plt.xlabel('Year')
plt.ylabel('volume ({})'.format(massUnit))
#plt.xticks(np.arange(22)*xtickSpacing)
plt.grid()
axX = axVol

axVAF = fig.add_subplot(nrow, ncol, 2, sharex=axX)
plt.xlabel('Year')
plt.ylabel('VAF ({})'.format(massUnit))
#plt.xticks(np.arange(22)*xtickSpacing)
plt.grid()

axVolGround = fig.add_subplot(nrow, ncol, 3, sharex=axX)
plt.xlabel('Year')
plt.ylabel('grounded volume ({})'.format(massUnit))
#plt.xticks(np.arange(22)*xtickSpacing)
plt.grid()

axVolFloat = fig.add_subplot(nrow, ncol, 4, sharex=axX)
plt.xlabel('Year')
plt.ylabel('floating volume ({})'.format(massUnit))
#plt.xticks(np.arange(22)*xtickSpacing)
plt.grid()

axGrdArea = fig.add_subplot(nrow, ncol, 5, sharex=axX)
plt.xlabel('Year')
plt.ylabel('grounded area (m$^2$)')
#plt.xticks(np.arange(22)*xtickSpacing)
plt.grid()

axFltArea = fig.add_subplot(nrow, ncol, 6, sharex=axX)
plt.xlabel('Year')
plt.ylabel('floating area (m$^2$)')
#plt.xticks(np.arange(22)*xtickSpacing)
plt.grid()

axGLflux = fig.add_subplot(nrow, ncol, 7, sharex=axX)
plt.xlabel('Year')
plt.ylabel('GL flux (kg/yr)')
#plt.xticks(np.arange(22)*xtickSpacing)
plt.grid()

axCalvFlux = fig.add_subplot(nrow, ncol, 8, sharex=axX)
plt.xlabel('Year')
plt.ylabel('calving flux (kg/yr)')
#plt.xticks(np.arange(22)*xtickSpacing)
plt.grid()


def VAF2seaLevel(vol):
    return vol * scaleVol / 3.62e14 * rhoi / rhosw 

def seaLevel2VAF(vol):
    return vol / scaleVol * 3.62e14 * rhosw / rhoi / 1000. 

def addSeaLevAx(axName):
    seaLevAx = axName.secondary_yaxis('right', functions=(VAF2seaLevel, seaLevel2VAF))
    seaLevAx.set_ylabel('Sea-level\nequivalent (m)')

def plotStat(fname, label, color, linestyle):
    print("Reading and plotting file: {}".format(fname))

    name = fname

    f = Dataset(fname,'r')
    yr = f.variables['daysSinceStart'][:]/365.0 + 2015.0
    print(yr.max())
    print(label)
    print(yr[-1])

    vol = f.variables['totalIceVolume'][:] / scaleVol
    axVol.plot(yr, vol[:]-vol[0], label=label, color=color, linestyle=linestyle)

    # vol = f.variables['totalIceVolume'][:] / scaleVol
    # axVol.plot(yr, vol, label=label, color=color, linestyle=linestyle)
    
    VAF = f.variables['volumeAboveFloatation'][:] / scaleVol       
    axVAF.plot(yr, (VAF[:]-VAF[0]), label=label, color=color, linestyle=linestyle)
    addSeaLevAx(axVAF)
    print(VAF[-1] * scaleVol / 3.62e14 * rhoi / rhosw * 1000.)
    print(VAF[0] * scaleVol / 3.62e14 * rhoi / rhosw * 1000.)
    print((VAF[-1]-VAF[0]) * scaleVol / 3.62e14 * rhoi / rhosw * 1000.)
    volGround = f.variables['groundedIceVolume'][:] / scaleVol
    axVolGround.plot(yr, volGround, label=label, color=color, linestyle=linestyle)

    volFloat = f.variables['floatingIceVolume'][:] / scaleVol
    axVolFloat.plot(yr, volFloat, label=label, color=color, linestyle=linestyle)

    areaGrd = f.variables['groundedIceArea'][:]
    axGrdArea.plot(yr, areaGrd, label=label, color=color, linestyle=linestyle)

    areaFlt = f.variables['floatingIceArea'][:]
    axFltArea.plot(yr, areaFlt, label=label, color=color, linestyle=linestyle)

    GLflux = f.variables['groundingLineFlux'][:]
    axGLflux.plot(yr, GLflux, label=label, color=color, linestyle=linestyle)

    calvFlux = f.variables['totalCalvingFlux'][:]
    axCalvFlux.plot(yr, calvFlux, label=label, color=color, linestyle=linestyle)


    f.close()


def plotStat2(fname, label, color, linestyle):
    print("Reading and plotting file: {}".format(fname))

    name = fname
    indx = 45
    f = Dataset(fname,'r')
    yr = f.variables['daysSinceStart'][:-indx]/365.0 + 2015.0
    print(yr.max())
    print(label)
    print(yr[-1])

    vol = f.variables['totalIceVolume'][:-indx] / scaleVol
    axVol.plot(yr, vol[:]-vol[0], label=label, color=color, linestyle=linestyle)

#     vol = f.variables['totalIceVolume'][:-indx] / scaleVol
#     axVol.plot(yr, vol, label=label, color=color, linestyle=linestyle)
    
    VAF = f.variables['volumeAboveFloatation'][:-indx] / scaleVol
    axVAF.plot(yr, (VAF[:]-VAF[0]), label=label, color=color, linestyle=linestyle)
    addSeaLevAx(axVAF)
    print(VAF[-1] * scaleVol / 3.62e14 * rhoi / rhosw * 1000.)

    volGround = f.variables['groundedIceVolume'][:-indx] / scaleVol
    axVolGround.plot(yr, volGround, label=label, color=color, linestyle=linestyle)

    volFloat = f.variables['floatingIceVolume'][:-indx] / scaleVol
    axVolFloat.plot(yr, volFloat, label=label, color=color, linestyle=linestyle)

    areaGrd = f.variables['groundedIceArea'][:-indx]
    axGrdArea.plot(yr, areaGrd, label=label, color=color, linestyle=linestyle)

    areaFlt = f.variables['floatingIceArea'][:-indx]
    axFltArea.plot(yr, areaFlt, label=label, color=color, linestyle=linestyle)

    GLflux = f.variables['groundingLineFlux'][:-indx]
    axGLflux.plot(yr, GLflux, label=label, color=color, linestyle=linestyle)

    calvFlux = f.variables['totalCalvingFlux'][:-indx]
    axCalvFlux.plot(yr, calvFlux, label=label, color=color, linestyle=linestyle)


    f.close()

#if (options.file1inName):
plotStat(options.file1inName, label="control coupled", color="red", linestyle="-")


if(options.file2inName):
   plotStat2(options.file2inName, label="control uncoupled", color="black", linestyle="-")

if(options.file3inName):
   plotStat(options.file3inName, label="NorESM-RCP2.6-repeat, coupled", color="blue",linestyle="-")

if(options.file4inName):
   plotStat(options.file4inName, label="NorESM-RCP2.6-repeat, uncoupled", color="blue",linestyle="--")

if(options.file5inName):
   plotStat(options.file5inName, label="CCSM4-RCP8.5, coupled", color="red",linestyle="-")

if(options.file6inName):
   plotStat(options.file6inName, label="CCSM4-RCP8.5, uncoupled", color="red",linestyle="--")

if(options.file7inName):
   plotStat(options.file7inName, label="UKESM-SSP5-85, coupled", color="m",linestyle="-")

if(options.file8inName):
   plotStat(options.file8inName, label="UKESM-SSP5-85, uncoupled", color="m",linestyle="--")

#if(options.file7inName):
#   plotStat(options.file7inName)

axCalvFlux.legend(loc='best', prop={'size': 6})

print("Generating plot.")
fig.tight_layout()
plt.show()


