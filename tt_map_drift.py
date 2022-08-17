from glob import glob
from datetime import datetime
import numpy as np
import pyresample as pr
import matplotlib.pyplot as plt
from tt_func import getColumn

outpath = '../plots_revision/'
outname='map_drift'

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

#plot drift of Co1, CO2, Co3
#put markers for each date we have transect

inpath = '../data/mosaic_buoy_data/selection/'
cofilelist = ['_co1.csv','_co2.csv','_co3.csv']
labels = ['MOSAiC CO1','MOSAiC CO2','MOSAiC CO3']
colors = ['blueviolet','tomato','fuchsia']

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
   
    ax.plot(x,y,lw=8,c=colors[i],alpha=0.8,label=labels[i])
    ax.plot(x,y,lw=1,c='k')

#N-ICE
#all 4 N-ICE floes
inpath = '../data/N-ICE/'
fnames = glob(inpath+'floe*_track.csv')

for fname in fnames:
    buoy = fname

    time = getColumn(buoy,0,skipheader=2)
    dt = [ datetime.strptime(time[x], "%Y-%m-%d %H:%M:%S") for x in range(len(time)) ]
    lat = np.asarray(getColumn(buoy,1,skipheader=2),dtype=float)
    lon = np.asarray(getColumn(buoy,2,skipheader=2),dtype=float)

    x,y = m(lon,lat)
    if buoy==fnames[0]:
        ax.plot(x,y,lw=8,c='0.5',alpha=0.8,label='N-ICE')
        ax.plot(x,y,lw=1,c='k')
    else:
        ax.plot(x,y,lw=8,c='0.5',alpha=0.8)
        ax.plot(x,y,lw=1,c='k')

#SHEBA
inpath = '../data/SHEBA/polon*/'
buoy = glob(inpath+'Microcat07100_separated')[0]
print(buoy)

lat = np.asarray(getColumn(buoy,2,skipheader=0),dtype=float)
lon = np.asarray(getColumn(buoy,3,skipheader=0),dtype=float)
lat = np.ma.array(lat,mask=lat==-999.99).compressed()
lon = np.ma.array(lon,mask=lon==-999.99).compressed()

x,y = m(lon,lat)
ax.plot(x,y,lw=8,c='0.25',alpha=0.8,label='SHEBA')
ax.plot(x,y,lw=1,c='k')

#W99 January as background color
from netCDF4 import Dataset
inpath_w99='../data/W99/'
fnames = sorted(glob(inpath_w99+'*.nc'))
f = Dataset(fnames[0])
lats = f.variables['latitude'][:]
lons = f.variables['longitude'][:]
sd = f.variables['snow_depth'][:]

x,y = m(lons,lats)
cs = ax.pcolor(x,y,sd,cmap=plt.cm.Blues,alpha=1,vmin=0,vmax=.5)
cb=plt.colorbar(cs,orientation='horizontal',pad=.01)
cb.set_label(label='January Climatological Snow Depth (m)',fontsize=30)

#larger ticks
cb.ax.tick_params(axis="x", labelsize=25)
cb.ax.tick_params(axis="y", labelsize=25)

#legend
ax.legend(loc='upper left',prop={'size':30}, fancybox=True, framealpha=0.8,numpoints=1)

fig1.savefig(outpath+outname,bbox_inches='tight')
plt.close()
