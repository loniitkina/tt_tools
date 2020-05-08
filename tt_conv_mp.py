import numpy as np
from glob import glob
from datetime import datetime, timedelta
from tt_func import *

outpath = '../data/'
path = '../../../MOSAiC/leg2_ICE/transect/'



flist = glob(path+'/*/*loop.dat')

flist = glob(path+'/*/*snow1.dat')

flist = glob(path+'/*/*runway*.dat')

flist = glob(path+'/*/*special*.dat')

#flist = glob(path+'/*/*ridge*.dat')

flist = glob(path+'/*/*BRUCE*special*.dat')

print(flist)
#exit()

for i in flist:
    #open data file
    fname = i
    print(fname)
    location = fname.split('/')[-1].split('.')[0]
    print(location)

    date = getColumn(fname,0, delimiter=',', magnaprobe=True)
    dc = [ date[x].split('.')[0] for x in range(len(date)) ]                        #get rid of the annoyting milliseconds (they appear only sometimes and break the datetime function in the next step)
    dt = [ datetime.strptime(dc[x], "%Y-%m-%d %H:%M:%S") for x in range(len(dc)) ]  #"2020-02-20 10:43:44"
    dt64 = np.array(dt, dtype='datetime64[s]')                                      #convert to array (different string format in output)
    
    #time on many AWI magnaprobes not UTC! (Anja is OK)
    name = fname.split('/')[-1].split('_')[0]
    print(name)
    if name == 'Katrin':
        dt64 = dt64 + np.timedelta64(6, 'h')
        
    if (name == 'BRUCE00') or (name == 'BRUCE01'):
        bruce = datetime(2000,5,23,7,51,23)
        cynthia = datetime(2020,1,7,7,53,0)
        diff = cynthia-bruce
        diff = int(diff.total_seconds())         #this is approximate and will require additional displacement in space
        
        #diff2 = (cynthia-bruce).days
        dt64 = dt64 + np.timedelta64(diff, 's')
        dt[0] = dt[0] + timedelta(seconds=diff) #to get the name right
        print(dt[0])
    
    lat1 = getColumn(fname,5, delimiter=',', magnaprobe=True)
    lat2 = getColumn(fname,14, delimiter=',', magnaprobe=True)
    if (name == 'BRUCE00') or (name == 'BRUCE01'): lat2 = getColumn(fname,13, delimiter=',', magnaprobe=True)
    lat1 = np.array(lat1,dtype=np.float)
    lat2 = np.array(lat2,dtype=np.float)
    lat = lat1+lat2
    #lat = np.array(lat)

    lon1 = getColumn(fname,7, delimiter=',', magnaprobe=True)
    lon2 = getColumn(fname,15, delimiter=',', magnaprobe=True)
    if (name == 'BRUCE00') or (name == 'BRUCE01'): lon2 = getColumn(fname,14, delimiter=',', magnaprobe=True)   #special treatment for Bruce :)
    lon1 = np.array(lon1,dtype=np.float)
    lon2 = np.array(lon2,dtype=np.float)
    lon = lon1+lon2
    #lon = np.array(lon)

    #write new csv file with time and coordinates only
    tt = [dt64,lat,lon]
    table = list(zip(*tt))

    outname = dt[0].strftime('%Y%m%d')+'_'+location+'_'+'MP_transect_track.csv'
    print(outname)
    with open(outpath+outname, 'wb') as f:
        np.savetxt(f, table, fmt="%s", delimiter=",")


#then convert coordinates by:
#python psref_gps2xy.py ../../transect/data/20200220_Sloop_MP_transect_track.csv ../dshipextracts/polarstern-ref-2020219to20200222.dat_short.txt
#python psref_gps2xy.py ../../transect/data/20200220_Sloop_MP_transect_track.csv ../dshipextracts/polarstern-ref-20191101to20200222.dat.txt

#gem-2 converts by
#python psref_gps2xy.py ../../../MOSAiC/thickness_workspace/01-ice-thickness/20191219_PS122-2_16-48/mosaic-transect-20191219-gem2-556-track.csv ../dshipextracts/polarstern-ref-20191101to20200222.dat.txt
