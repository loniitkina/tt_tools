import sys
from glob import glob
from icedrift import GeoReferenceStation, IceCoordinateSystem, GeoPositionData
import matplotlib.pyplot as plt 
from tt_func import *

leg=4

instrument='magnaprobe'
path = '../data/MCS/MP/'
#valid locations are:
#leg 1: Nloop, Sloop
#leg 2: Nloop, Sloop, snow1, runway, special (long, dark side FYI/SYI,recon), ridgeFR1 (installation), ridgeFR2 (coring), ridgeFR3 (optics), ridgeA1 (center), ridgeA2 (N), ridgeA3 (S)
#leg 3: Nloop, Sloop, snow1, ridgeFR1 (installation), ridgeA1 (center), ridgeA2 (N), ridgeA3 (S), ridgeD (davids), ridgeE (eco), special
#leg 4: icestation, transect, ridge, albedoLD, albedoRBB, special (meltponds, drillholes, initialsurvey), ARIEL
#leg 5: transect(Kinder), ridge, ARIEL, kuka, special (transectstbd,transectbow,transectport,transectgrid), icestation1, icestation2, icestation3
#location = 'ridge*'
#location = 'Nloop'
location = 'transect*'
#location = 'albedo*'
#location = 'ARIEL'
#location='initialsurvey'
latlon=False

instrument='mosaic*'     #this is GEM-2 for some reason
path = '../data/MCS/GEM2_thickness/01-ice-thickness/'
#path = '../data/MCS/01-ice-thickness/'
location='' #no locations for GEM-2
latlon=True #GEM-2 data is written as latlon and not lonlat

#reference position file
#Floenavi
#refstat_csv_file = glob('../data/floenavi/data_master-solution_mosaic-leg'+str(leg)+'*-floenavi-refstat-v1p0.csv')[0]
#floenavi alternatives bellow (PS GPS data with ship heading)
#refstat_csv_file = '../../coord_trans/dshipextracts/transect_legs/position_leg3_nh-track.csv'
refstat_csv_file = '../../coord_trans/dshipextracts/transect_legs/position_leg4_nh-track.csv'
#refstat_csv_file = '../../coord_trans/dshipextracts/transect_legs/position_leg5_nh-track.csv'

refstat = GeoReferenceStation.from_csv(refstat_csv_file)
icecs = IceCoordinateSystem(refstat)

#get data for which you need coordinate transformation
all_transect_files = sorted(glob(path+'*PS122-'+str(leg)+'*/'+instrument+'-*-20200716*'+location+'-track.csv'))

##for Nloop on 20200403 and 06 the conversion from floenavi is bad
#all_transect_files = sorted(glob(path+'*PS122-'+str(leg)+'*/'+instrument+'-transect-20200403*'+location+'-track.csv'))
#all_transect_files = sorted(glob(path+'*PS122-'+str(leg)+'*/'+instrument+'-transect-20200406*'+location+'-track.csv'))
##for Sloop on 20200406 the conversion from floenavi is bad
#all_transect_files = sorted(glob(path+'*PS122-'+str(leg)+'*/'+instrument+'-transect-20200406*'+location+'-track.csv'))

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
