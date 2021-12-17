import numpy as np
from glob import glob
import os
from datetime import datetime, timedelta
from tt_func import *

#prepare position data for floenavi from RTKPost text files (GNSS base stations)

station='base3_P7'
name='2019I3'

path = '../data/buoys/'
flist = glob(path+name+'*.csv')
print(flist)

for i in flist:
    #open data file
    fname = i
    print(fname)

    lon = getColumn(fname,2)
    lat = getColumn(fname,1)    
    lat = np.array(lat,dtype=np.float)
    lon = np.array(lon,dtype=np.float)
    
    date = getColumn(fname,0)
    dt = [ datetime.strptime(date[x], "%Y-%m-%dT%H:%M:%S") for x in range(len(date)) ]
    
    year = [ datetime.strftime(dt[x], "%Y") for x in range(len(dt)) ]
    month = [ datetime.strftime(dt[x], "%m") for x in range(len(dt)) ]
    day = [ datetime.strftime(dt[x], "%d") for x in range(len(dt)) ]
    
    
    
    #write new csv file with time and coordinates only
    tt = [year,month,day,lon,lat]
    table = list(zip(*tt))

    outname = fname.split('.csv')[0]+'-track.csv'
    print(outname)
    with open(outname, 'wb') as f:
        header = ['year,month,day,longitude,latitude']
        np.savetxt(f, header, fmt="%s", delimiter=",")
        np.savetxt(f, table, fmt="%s", delimiter=",")


