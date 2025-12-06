import numpy as np
from osgeo import gdal, osr
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from datetime import datetime
from glob import glob
from tt_func import getColumn, proj_sat
import gc

outpath='../data/MicroSHIFT/'
outpath_plots='../plots_microshift/'
inpath_table = outpath

#selected reference date: 20200116

#orthophoto
#time: 20250511T17 (during bingo)
tif=outpath+'drone_composite_20250511_geocoded_clip_low.tif'  #cropped in QGIS by Raster Clipper
outname='MicroSHIFT_transects_overview_c.png'

##refstation
##reference heading in Floenavi: 301.63560882616076
##2025-05-11 17:01:00,19.90130185,83.88559853333334,330.07
lon0=19.90130185
lat0=83.88559853333334
head0=330.07

minx = -100;maxx = 300
miny = -300;maxy = 10
xsize=35;ysize=20

shiftx=-75;shifty=-30

##RS-2 image
#tif=outpath+'RS2_20250516_124249_0004_FQ7_HHVVHVVH_SLC_1211282_2748_103620642_comp.tif'
#outname='MicroSHIFT_transects_overview_RS2.png'
##20250516_124249: 2025-05-16 12:42:00	20.4004331833333	83.68815775	326.29
#lon0=20.4004331833333
#lat0=83.68815775
#head0=326.29

#minx = -5000;maxx = 5000
#miny = -5000;maxy = 5000
#xsize=20;ysize=17

#shiftx=-10;shifty=35

#image coordinate conversion to local coordinates
red,rot_x,rot_y=proj_sat(tif,lon0,lat0,head0,spacing=1,band=1,alos=False)

#setup figure
fig1 = plt.figure(figsize=(xsize,ysize))  #a bit shorter to compensate for the colorbar at the side

ax = fig1.add_subplot(111)
CS = plt.pcolormesh(rot_x, rot_y, red.T, vmin=0, vmax=250, cmap=plt.cm.binary_r)

#limit the region
ax.set_xlim(minx,maxx)
ax.set_ylim(miny,maxy)

#ground transects

#just first transects
flist = glob(inpath_table+'**/magna+gem2*_2_multif.csv')#+['../data/MicroSHIFT/20250510_ridge_recon/mosaic_gem-2+mp_20250510_recon_2.csv']
flist.sort()

for i in range(0,len(flist)):
    
    fname = flist[i]
    print(fname)
    if fname=='../data/MicroSHIFT/20250530_bonus_station/magna+gem2_20250530_bonus_2_multif.csv': continue
    
    xx = getColumn(fname,3, delimiter=',')
    xx = np.array(xx,dtype=np.float)
    
    yy = getColumn(fname,4, delimiter=',')
    yy = np.array(yy,dtype=np.float)
    
    #Ice Thickness f5325Hz_hcp_i for ridge files and 18kHz for level ice transects
    it = getColumn(fname,8, delimiter=',')
    it = np.array(it,dtype=np.float)
    
    ic = getColumn(fname,14, delimiter=',')
    ic = np.array(ic,dtype=np.float)
    
    #Snow Depth
    sd = getColumn(fname,5, delimiter=',')
    sd = np.array(sd,dtype=np.float)
    #if sd[0]==0: continue       #recon data has snow depth at constant 0, do not plot!
    
    #adjust the individual profiles
    xx=xx-shiftx
    yy=yy+shifty
    
    #ice thickness
    #imap = ax.scatter(xx,yy,c=it,s=10,cmap=plt.cm.Reds,vmin=0,vmax=5)
    
    ##some offset for the snow
    #xx=xx+2
    #yy=yy+2
    #imap = ax.scatter(xx,yy,c=sd,s=10,cmap=plt.cm.Blues,vmin=0,vmax=1)
    
    #consolidated layer ratio
    #xx=xx+2
    #yy=yy+2
    imap = ax.scatter(xx,yy,c=it/ic,s=10,cmap=plt.cm.Purples,vmin=0.8,vmax=1)

#cb = plt.colorbar(imap, ax=ax, pad=.01)
#cb.set_label(label='Sea ice thickness (m)',fontsize=20)
#cb.ax.tick_params(labelsize=20)

#cb = plt.colorbar(imap, ax=ax, pad=.01)
#cb.set_label(label='Snow depth (m)',fontsize=20)
#cb.ax.tick_params(labelsize=20)

cb = plt.colorbar(imap, ax=ax, pad=.01)
cb.set_label(label='Consolidated ice fraction',fontsize=20)
cb.ax.tick_params(labelsize=20)

plt.show()
fig1.savefig(outpath_plots+outname,bbox_inches='tight')
plt.close(fig1)
