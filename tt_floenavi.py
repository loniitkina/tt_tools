import sys
from glob import glob
from icedrift import GeoReferenceStation, IceCoordinateSystem, GeoPositionData
import matplotlib.pyplot as plt 
from tt_func import *

leg=3   #currently 1-3 are available (4 pending!)
#valid locations are:
#leg 1: Nloop, Sloop
#leg 2: Nloop, Sloop, snow1, runway, special, ridgeFR1 (installation), ridgeFR2 (coring), ridgeFR3 (optics), ridgeA1 (center), ridgeA2 (N), ridgeA3 (S)
#leg 3: Nloop, Sloop, snow1, ridgeFR1 (installation), ridgeA1 (center), ridgeA2 (N), ridgeA3 (S), ridgeD (davids), ridgeE (eco), special
location = 'ridge*'
path = '../data/MCS/MP/'

#reference position file
refstat_csv_file = glob('../data/floenavi/data_master-solution_mosaic-leg'+str(leg)+'*-floenavi-refstat-v1p0.csv')[0]
refstat = GeoReferenceStation.from_csv(refstat_csv_file)
icecs = IceCoordinateSystem(refstat)

#get data for which you need coordinate transformation
all_transect_files = sorted(glob(path+'PS122-'+str(leg)+'*/magnaprobe-transect-*'+location+'-track.csv'))

plt.figure(figsize=(10, 10))
plt.gca().set_aspect('equal')

for i, track_csv_filepath in enumerate(all_transect_files):
    print(i)
    print(track_csv_filepath)
    name = track_csv_filepath.split('/')[-1]
    
    pos = GeoPositionData.from_csv(track_csv_filepath, header=None)
    icepos = icecs.get_xy_coordinates(pos)
    plt.scatter(icepos.xc, icepos.yc, s=20-i*2, label=name)
    
    #store these data in a csv file
    date = getColumn(track_csv_filepath,0, delimiter=',')
    lon = getColumn(track_csv_filepath,1, delimiter=',')
    lat = getColumn(track_csv_filepath,2, delimiter=',')
    xc = icepos.xc
    yc = icepos.yc
    
    tt = [date,lon,lat,xc,yc]
    table = list(zip(*tt))
    
    outname = track_csv_filepath.split('.csv')[0]+'-icecs-xy.csv'
    print(outname)
    with open(outname, 'wb') as f:
        np.savetxt(f, table, fmt="%s", delimiter=",")
    
plt.grid()
plt.legend()
plt.show()
