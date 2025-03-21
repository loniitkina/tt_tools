import csv
import re
from glob import glob
from datetime import datetime
import numpy as np
import pyresample as pr
import matplotlib.pyplot as plt
from tt_func import getColumn

outpath = '../plots_sm/'
outname='map_drift_snowmodel'

#Set up a map plot
fig1    = plt.figure(figsize=(20,20))
ax      = fig1.add_subplot(111)
area_def = pr.utils.load_area('area.cfg', 'arctic')  
m = pr.plot.area_def2basemap(area_def)
m.drawmapboundary(fill_color='#9999FF')
m.drawcoastlines()
m.fillcontinents(color='#ddaa66',lake_color='#9999FF')
#m.bluemarble(scale=.25)
##Draw parallels and meridians
m.drawparallels(np.arange(60.,86.,5),latmax=85.)
m.drawmeridians(np.arange(-180.,180.,20.),latmax=85.)


#SnowModel parcel
inpath = '../../snow_model/mosaic_ship_2023/1_nloop/1_sm/1_ship_track/8_mk_final_parcel_ll/'
fname = inpath+'parcel_ll_space.dat'    #added space as first sign in each row
print(fname)

results = csv.reader(open(fname))
lon = [re.sub(" +", " ",row[0]) for row in results]
lon = np.array(lon,dtype=np.float)
#print(lon)

results = csv.reader(open(fname))
#get rid of all multi-white spaces and split in those that remain
results_clean = [re.sub(" +", " ",row[1]) for row in results]
lat = [row.split(" ")[1] for row in results_clean]
lat = np.array(lat,dtype=np.float)
#print(lat)

x,y = m(lon,lat)
ax.plot(x,y,lw=8,c='0.25',alpha=0.8,label='SnowModel')
ax.plot(x,y,lw=1,c='k')

#plot drift of Co1, CO2, Co3
#put markers for each date we have transect
inpath = '../data/mosaic_buoy_data/selection/'
cofilelist = ['_co1.csv','_co2.csv']
labels = ['MOSAiC CO1','MOSAiC CO2']
colors = ['blueviolet','tomato']

for i in range(0,len(cofilelist)):
    buoy = glob(inpath+'*'+cofilelist[i])[0]

    time = getColumn(buoy,0)
    dt = [ datetime.strptime(time[x], "%Y-%m-%d %H:%M:%S") for x in range(len(time)) ]
    lon = np.asarray(getColumn(buoy,1),dtype=float)
    lat = np.asarray(getColumn(buoy,2),dtype=float)
    
    #get rid of all those faulty zeros
    mask= (lon==0) | (lat==0)
    lon = np.ma.array(lon,mask=mask).compressed()
    lat = np.ma.array(lat,mask=mask).compressed()

    x,y = m(lon,lat)
   
    ax.plot(x,y,lw=6,c=colors[i],alpha=0.8,label=labels[i])
    ax.plot(x,y,lw=1,c='k')

#The buoy that was used in SnowModel

inpath = '../../snow_model/mosaic_ship_2023/1_nloop/1_sm/1_ship_track/1_orig/'
buoy = inpath+'2019I3_300434063387850_AUX_proc_clean.csv'


time = getColumn(buoy,0)
dt = [ datetime.strptime(time[x], "%Y-%m-%dT%H:%M:%S") for x in range(len(time)) ]
lon = np.asarray(getColumn(buoy,2),dtype=float)
lat = np.asarray(getColumn(buoy,1),dtype=float)

#get rid of all those faulty zeros
mask= (lon==0) | (lat==0)
lon = np.ma.array(lon,mask=mask).compressed()
lat = np.ma.array(lat,mask=mask).compressed()

x,y = m(lon,lat)

#ax.plot(x,y,lw=6,c=colors[i],alpha=0.8,label=labels[i])
ax.plot(x,y,lw=2,c='.75',label='buoy')


##W99 January as background color
#from netCDF4 import Dataset
#inpath_w99='../data/W99/'
#fnames = sorted(glob(inpath_w99+'*.nc'))
#f = Dataset(fnames[0])
#lats = f.variables['latitude'][:]
#lons = f.variables['longitude'][:]
#sd = f.variables['snow_depth'][:]

#x,y = m(lons,lats)
#cs = ax.pcolor(x,y,sd,cmap=plt.cm.Blues,alpha=1,vmin=0,vmax=.5)
#cb=plt.colorbar(cs,orientation='horizontal',pad=.01)
#cb.set_label(label='January Climatological Snow Depth (m)',fontsize=30)

##larger ticks
#cb.ax.tick_params(axis="x", labelsize=25)
#cb.ax.tick_params(axis="y", labelsize=25)

#legend
ax.legend(loc='upper left',prop={'size':30}, fancybox=True, framealpha=0.8,numpoints=1)

plt.show()
fig1.savefig(outpath+outname,bbox_inches='tight')
plt.close()
