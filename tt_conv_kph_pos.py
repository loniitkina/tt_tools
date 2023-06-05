import numpy as np
from glob import glob
import os
from datetime import datetime, timedelta
from tt_func import getColumn

#convert KPH log file to base station to floenavi format (that tt_tools can read)

station='breathe'

path='../data/breathe/coring/'

flist = glob(path+'pos18-05-2023.csv')
date = '20230518'

print(flist)

for i in flist:
    #open data file
    fname = i
    print(fname)

    lon = getColumn(fname,6, delimiter=',',skipheader=3)
    lat = getColumn(fname,5, delimiter=',',skipheader=3)
    heading = getColumn(fname,8, delimiter=',',skipheader=3)
    heading= np.array(heading,dtype=np.float)
    
    #convert from digital minutes to digital degrees
    lat1 = [ x[:2] for x in lat ]
    lat2 = [ x[2:12] for x in lat ]
    lat1 = np.array(lat1,dtype=np.float)
    lat2 = np.array(lat2,dtype=np.float)/60
    lat = lat1 + lat2
    
    lon1 = [ x[:3] for x in lon ]
    lon2 = [ x[3:13] for x in lon ]
    lon1 = np.array(lon1,dtype=np.float)
    lon2 = np.array(lon2,dtype=np.float)/60
    lon = lon1 + lon2
    
    
    
    time = getColumn(fname,1, delimiter=',',skipheader=3)
    date = [ date+'T'+x for x in time ]
    dt = [ datetime.strptime(x, "%Y%m%dT%H:%M:%S") for x in date ]
    
    date = [ datetime.strftime(x, '%Y-%m-%d %H:%M:%S') for x in dt ]
    
    #write new csv file with time and coordinates only
    tt = [date,lon,lat,heading]
    table = list(zip(*tt))

    outname = fname.split('.csv')[0]+'-track.csv'
    print(outname)
    with open(outname, 'wb') as f:
        header = ['time,longitude,latitude,heading,origin_uncertainty_m,heading_uncertainty_deg']
        np.savetxt(f, header, fmt="%s", delimiter=",")
        np.savetxt(f, table, fmt="%s", delimiter=",")
