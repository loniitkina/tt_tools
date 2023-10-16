import numpy as np
from osgeo import gdal, osr
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from datetime import datetime
from glob import glob
from tt_func import getColumn, proj_sat, floenavi_coords_buoy
import gc


#reference heading in Floenavi: 301.63560882616076
#on 20/2/2020: 266.5130272362738 >> 40 deg difference!

outpath='../plots_sm/'

#RS-2 scene for 31 Dec 2019, 03:35:02 UTC
tif='../data/RS-2_Wenkai/RS2_20191231_033502_0004_FQ20W_HHVVHVVH_SLC_783865_1107_32077288_HV.tif'
alos=False

#ref station:
#2019-12-30 23:57:00,117.55830668564211,86.5764168341106,301.09810246611045,6.524323286537021,1.2599949267618238
#2019-12-31 11:18:00,117.86992035257677,86.58894049718843,302.9781616061306,5.396583432095628,0.9740373134474475
#2019/12/31 11:18:00	117.877961	86.588972	207.9
#lon0=117.86992035257677
#lat0=86.58894049718843
#head0=302.9781616061306
##difference in x,y
#0.0023430867721458927 0.0555309670589043
#53.43683464292577 3.5778224217515917
#2019/12/31 03:35:02	117.704953	86.578373	207.2
lon0=117.704953
lat0=86.578373
head0=302.2

arr,rot_x,rot_y=proj_sat(tif,lon0,lat0,head0,spacing=1,band=1,ps_pos=True)

#Wenkai masks no values as 999
arr = np.where(arr==999,0,arr)

#setup figure
fig1 = plt.figure(figsize=(20,12))
ax = fig1.add_subplot(111)

##for TSX and RS-2
CS1=ax.contourf(rot_x, rot_y, arr.T, 50,cmap=plt.cm.binary_r)
cb = plt.colorbar(CS1)  # draw colorbar
cb.set_label(label='Intensity (dB)',fontsize=20)

#limit the region
ax.set_xlim(-6000,4000)
ax.set_ylim(-6000,6000)

#larger ticks
ax.tick_params(axis="x", labelsize=18)
ax.tick_params(axis="y", labelsize=18)

#del arr, rot_x, rot_y
gc.collect()
            
#buoy locations at the end of the winter
fnames = sorted(glob('../data/mosaic_buoy_data/selection/*_locs.csv'))
outname='RS2_20191231_map_buoys_all.png'

inpath = '../data/mosaic_buoy_data/selection/'
fnames = glob(inpath+'2019P103*_locs.csv')+\
    glob(inpath+'2019P193*_locs.csv')+\
    glob(inpath+'2019P195*_locs.csv')+\
    glob(inpath+'2019P204*_locs.csv')
outname='RS2_20191231_map_buoys4.png'

#fnames = glob(inpath+'2019P158*_locs.csv')+\
    #glob(inpath+'2019P201*_locs.csv')+\
    #glob(inpath+'2019P204*_locs.csv')+\
    #glob(inpath+'2019P193*_locs.csv')
#outname='RS2_20191231_map_buoys4a.png'

colors = plt.cm.jet(np.linspace(0, 1, len(fnames)))

#ref station:
#2020-05-10 23:57:00,13.198624043223964,83.58067010547973,189.69703458250768,5.422929366192587,
refdt = datetime(2020,5,10,23,57,0)
lon0=13.198624043223964
lat0=83.58067010547973
head0=189.69703458250768


##2019-12-31 11:18:00,117.86992035257677,86.58894049718843,302.9781616061306,5.396583432095628,0.9740373134474475
#refdt = datetime(2019,12,31,11,18,0)
#lon0=117.86992035257677
#lat0=86.58894049718843
#head0=302.9781616061306
#outname='RS2_20191231_map_buoys_early.png'

import warnings
warnings.filterwarnings("ignore")

for i in range(0,len(fnames)):
    fname = fnames[i]
    buoy = fname.split('/')[-1].split('_')[0]
    
    dt = getColumn(fname,0)
    dt = [ datetime.strptime(x, "%Y-%m-%d %H:%M:%S") for x in dt ]
    lon = getColumn(fname,1)
    lon = np.array(lon,dtype=np.float)
    lat = getColumn(fname,2)
    lat = np.array(lat,dtype=np.float)
    
    x,y = floenavi_coords_buoy(dt,lon,lat,refdt,lon0,lat0,head0)
    
    if (abs(x)<10000) & (abs(y)<10000):
        print(fname)
        print(x,y)
        ax.plot(x,y,'o',ms=15,c=colors[i],label=buoy)

ax.legend()

plt.show()
fig1.savefig(outpath+outname,bbox_inches='tight')
