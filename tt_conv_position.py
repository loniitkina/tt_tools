import numpy as np
from glob import glob
import os
from datetime import datetime, timedelta
from tt_func import *

leg = 5
path = '../../coord_trans/dshipextracts/transect_legs/'
flist = glob(path+'position_leg'+str(leg)+'_nh.dat')

for i in flist:
    #open data file
    fname = i
    print(fname)

    lon = getColumn(fname,1, delimiter='\t')
    lat = getColumn(fname,2, delimiter='\t')
    heading = getColumn(fname,3, delimiter='\t')

    if leg < 4:
        ssample=0   #full minute seconds
        
    else:
        ssample=51  #full minute seconds (if 1-minute data is requested)
    
    lat = np.array(lat,dtype=np.float)
    lon = np.array(lon,dtype=np.float)
    heading = np.array(heading,dtype=np.float)

    date = getColumn(fname,0, delimiter='\t')
    dt = [ datetime.strptime(date[x], "%Y/%m/%d %H:%M:%S") for x in range(len(date)) ]
    
    #1-min position/time is enough
    dt64 = np.array(dt, dtype='datetime64[s]')
    seconds = [ x.second for x in dt ]
    seconds = np.array(seconds)
    #print(seconds)
    mask = seconds!=ssample
    dt64 = np.ma.array(dt64,mask=mask); dt64=dt64.compressed()
    lon = np.ma.array(lon,mask=mask); lon=lon.compressed()
    lat = np.ma.array(lat,mask=mask); lat=lat.compressed()
    heading = np.ma.array(heading,mask=mask); heading=heading.compressed()
    
    dt = dt64.tolist()
    date = [ datetime.strftime(x, '%Y-%m-%d %H:%M:%S') for x in dt ]
    
    #write new csv file with time and coordinates only
    tt = [date,lon,lat,heading]
    table = list(zip(*tt))

    outname = fname.split('.dat')[0]+'-track.csv'
    print(outname)
    with open(outname, 'wb') as f:
        #add header manually afterwards:
        #time,longitude,latitude,heading,origin_uncertainty_m,heading_uncertainty_deg
        np.savetxt(f, table, fmt="%s", delimiter=",")


