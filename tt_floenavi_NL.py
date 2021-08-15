import sys
from glob import glob
from icedrift import GeoReferenceStation, IceCoordinateSystem, GeoPositionData
import matplotlib.pyplot as plt 
from tt_func import *

#instrument='magnaprobe'
#path = '../data/NansenLegacy/magnaprobe/'
#location='P4'
#latlon=False

instrument='transect*'     #this is GEM-2 for some reason
path = '../data/NansenLegacy/gem2/'
location='' #no locations for GEM-2
latlon=True #GEM-2 data is written as latlon and not lonlat

#reference position file
refstat_csv_file = '../data/NansenLegacy/position/garmin_transect_P4_2021-05-05.csv-track.csv'

refstat = GeoReferenceStation.from_csv(refstat_csv_file)
icecs = IceCoordinateSystem(refstat)

#get data for which you need coordinate transformation
all_transect_files = sorted(glob(path+instrument+'*'+location+'-track.csv'))

plt.figure(figsize=(10, 10))
plt.gca().set_aspect('equal')

for i, track_csv_filepath in enumerate(all_transect_files):
    print(i)
    print(track_csv_filepath)
    name = track_csv_filepath.split('/')[-1]
    
    try:
        pos = GeoPositionData.from_csv(track_csv_filepath, header=None, latlon=latlon)
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
    except:
        continue
    
plt.grid()
plt.legend()
plt.show()