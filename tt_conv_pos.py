import numpy as np
from glob import glob
import os
from datetime import datetime, timedelta
from tt_func import *

#prepare position data for floenavi from RTKPost text files (GNSS base stations)

station='base3_P7'
date='2021-05-13'

path = '../data/NansenLegacy/position/'
flist = glob(path+station+'*'+date+'.pos')
print(flist)

for i in flist:
    #open data file
    fname = i
    print(fname)

    lon = getColumn(fname,2, delimiter=',',rtkpost=True)
    lat = getColumn(fname,1, delimiter=',',rtkpost=True)    
    lat = np.array(lat,dtype=np.float)
    lon = np.array(lon,dtype=np.float)
    
    date = getColumn(fname,0, delimiter=',',rtkpost=True)
    dt = [ datetime.strptime(date[x], "%Y/%m/%d %H:%M:%S.000") for x in range(len(date)) ]
        
    #1-min position/time is enough
    ssample=0
    dt64 = np.array(dt, dtype='datetime64[s]')
    seconds = [ x.second for x in dt ]
    seconds = np.array(seconds)
    #print(seconds)
    mask = seconds!=ssample
    dt64 = np.ma.array(dt64,mask=mask); dt64=dt64.compressed()
    lon = np.ma.array(lon,mask=mask); lon=lon.compressed()
    lat = np.ma.array(lat,mask=mask); lat=lat.compressed()
    
    dt = dt64.tolist()
    
    date = [ datetime.strftime(x, '%Y-%m-%d %H:%M:%S') for x in dt ]
    
    #arbitrary heading
    heading = np.zeros_like(lon)
    
    #write new csv file with time and coordinates only
    tt = [date,lon,lat,heading]
    table = list(zip(*tt))

    outname = fname.split('.pos')[0]+'-track.csv'
    print(outname)
    with open(outname, 'wb') as f:
        header = ['time,longitude,latitude,heading,origin_uncertainty_m,heading_uncertainty_deg']
        np.savetxt(f, header, fmt="%s", delimiter=",")
        np.savetxt(f, table, fmt="%s", delimiter=",")


