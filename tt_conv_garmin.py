import numpy as np
from glob import glob
import os
from datetime import datetime, timedelta
from tt_func import *

#to convert from gpx to csv use gpx-converter
#https://pypi.org/project/gpx-converter/
#pip install -U gpx-converter

#from gpx_converter import Converter
#Converter(input_file='2021-05-05 07.23.38 Auto.gpx').gpx_to_csv(output_file='your_output.csv')

station='P4'
date='2021-05-05'

station='P5'
date='2021-05-08'

#station='P6'
#date='2021-05-10'

#station='P7'
#date='2021-05-14'

path = '../data/NansenLegacy/position/'
flist = glob(path+'garmin_transect_'+station+'*'+date+'.csv')

print(flist)

for i in flist:
    #open data file
    fname = i
    print(fname)

    lon = getColumn(fname,2, delimiter=',')
    lat = getColumn(fname,1, delimiter=',')
    #heading = getColumn(fname,3, delimiter='\t')

    #if leg < 4:
        #ssample=0   #full minute seconds
        
    #else:
        #ssample=51  #full minute seconds (if 1-minute data is requested)
    
    lat = np.array(lat,dtype=np.float)
    lon = np.array(lon,dtype=np.float)
    #heading = np.array(heading,dtype=np.float)

    date = getColumn(fname,0, delimiter=',')
    dt = [ datetime.strptime(date[x], "%Y-%m-%d %H:%M:%S+00:00") for x in range(len(date)) ]
    
    ##1-min position/time is enough
    #dt64 = np.array(dt, dtype='datetime64[s]')
    #seconds = [ x.second for x in dt ]
    #seconds = np.array(seconds)
    ##print(seconds)
    #mask = seconds!=ssample
    #dt64 = np.ma.array(dt64,mask=mask); dt64=dt64.compressed()
    #lon = np.ma.array(lon,mask=mask); lon=lon.compressed()
    #lat = np.ma.array(lat,mask=mask); lat=lat.compressed()
    #heading = np.ma.array(heading,mask=mask); heading=heading.compressed()
    
    #dt = dt64.tolist()
    
    date = [ datetime.strftime(x, '%Y-%m-%d %H:%M:%S') for x in dt ]
    
    #arbitrary heading
    heading = np.zeros_like(lon)
    
    #write new csv file with time and coordinates only
    tt = [date,lon,lat,heading]
    table = list(zip(*tt))

    outname = fname.split('.dat')[0]+'-track.csv'
    print(outname)
    with open(outname, 'wb') as f:
        header = ['time,longitude,latitude,heading,origin_uncertainty_m,heading_uncertainty_deg']
        np.savetxt(f, header, fmt="%s", delimiter=",")
        np.savetxt(f, table, fmt="%s", delimiter=",")


