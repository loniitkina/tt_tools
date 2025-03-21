import numpy as np
from osgeo import gdal, osr
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from datetime import datetime
from glob import glob
from tt_func import getColumn, proj_sat
import gc

outpath='../data/ridges/'
outpath_plots='../plots_ridges/'

#ALS tif from 21 Jan >>> first ALS available after Alli's ridge formation
#time: 20200121T103544-20200121T103614 to 20200121T121616-20200121T121646
tif='../data/ALS/20200121_als_merged_grid-stere_clip_CO_small.tif'  #cropped in QGIS by Raster Clipper - only CO
tif='../data/ALS/20200121_als_merged_grid-stere_clip_CO_rot.tif'

#refstation
#reference heading in Floenavi: 301.63560882616076
#2020-01-21 10:35:00,96.16950957480864,87.48817329565784,284.55644100627484,3.348816529475723,0.686339670008361
lon0=96.16950957480864
lat0=87.48817329565784
head0=284.55644100627484

arr,rot_x,rot_y=proj_sat(tif,lon0,lat0,head0,spacing=1,band=1,alos=False)

#setup figure
fig1 = plt.figure(figsize=(20,10))

ax = fig1.add_subplot(111)
#do something about the PS (too high!)
arr = np.where(arr>3.,3.,arr)
#smooth the level areas 
arr = np.where(arr<.1,0,arr)
#CS = plt.contourf(rot_x, rot_y, arr.T, 30, vmax=1., vmin=0,cmap=plt.cm.binary_r,alpha=.5)
CS = plt.contourf(rot_x, rot_y, arr.T, 30, vmax=2., vmin=0,alpha=.5)

#limit the region - CO
ax.set_xlim(-1350,1850)
ax.set_ylim(-830,1100)
ax.set_ylim(-1000,1100)

#magnaprobe transects
#selected reference date: 20200116
inpath_table = '../data/ridges_multif/'

#October transects
flist = [inpath_table+'mosaic_gem-2+mp_20191024_Nloop_2.csv',inpath_table+'mosaic_gem-2+mp_20191031_Nloop_2.csv',inpath_table+'mosaic_gem-2+mp_20191031_Sloop_2.csv']
outname='ALS_20200121_ridge_transects_consoli_oct.png'


#December transects - 2.7km
#flist = [inpath_table+'mosaic_gem-2+mp_20191205_Sloop_2.csv',inpath_table+'mosaic_gem-2+mp_20191205_Nloop_2.csv']
#outname='ALS_20200121_ridge_transects_consoli_dec.png'

#January transects - 21.5km
#flist = glob(inpath_table+'mosaic_gem-2+mp_202001*.csv')
#outname='ALS_20200121_ridge_transects_consoli_jan.png'

#February transects - 26.8km
#flist = glob(inpath_table+'mosaic_gem-2+mp_202002*.csv')
#outname='ALS_20200121_ridge_transects_consoli_feb.png'

##March transects - 4.2km
#flist = [inpath_table+'mosaic_gem-2+mp_20200305_Sloop_2.csv',inpath_table+'mosaic_gem-2+mp_20200305_Nloop_2.csv',
         #inpath_table+'mosaic_gem-2+mp_20200326_Nloop_2.csv']
#outname='ALS_20200121_ridge_transects_consoli_mar.png'

##April transects - any sense? Maybe just the Nloop  - 1.3km
#flist = [inpath_table+'mosaic_gem-2+mp_20200430_Nloop_2.csv']
#outname='ALS_20200121_ridge_transects_consoli_apr.png'

##June/July - 3.6km
#flist = [inpath_table+'mosaic_gem-2+mp_20200630_transect_2.csv']#,inpath_table+'mosaic_gem-2+mp_20200629_transect_2.csv']
#outname='ALS_20200121_ridge_transects_consoli_jun.png'

##none
#flist = []
#outname='ALS_20200121_ridge_transects_overview.png'
#cb = plt.colorbar(CS, ax=ax, pad=.01)  # draw colorbar
##cb.set_label(label='Intensity (dB)',fontsize=20)
#cb.set_label(label='Elevation (m)',fontsize=20)
#cb.ax.tick_params(labelsize=20)

flist.sort()

distance=[]

for i in range(0,len(flist)):
    
    fname = flist[i]
    print(fname)
    date = fname.split('_')[-3]
    loc = fname.split('_')[-2]
    print(date)
    print(loc)
    
    xx = getColumn(fname,3, delimiter=',')
    xx = np.array(xx,dtype=np.float)
    
    yy = getColumn(fname,4, delimiter=',')
    yy = np.array(yy,dtype=np.float)
    
    it1 = np.array(getColumn(fname,6),dtype=np.float)
    it2 = np.array(getColumn(fname,7),dtype=np.float)
    it3 = np.array(getColumn(fname,8),dtype=np.float)
    it4 = np.array(getColumn(fname,9),dtype=np.float)
    it5 = np.array(getColumn(fname,10),dtype=np.float)
    it6 = np.array(getColumn(fname,11),dtype=np.float)
    it7 = np.array(getColumn(fname,12),dtype=np.float)
    it8 = np.array(getColumn(fname,13),dtype=np.float)
    it9 = np.array(getColumn(fname,14),dtype=np.float)
    it10 = np.array(getColumn(fname,15),dtype=np.float)
    
    ii = np.empty((2,len(it3)))
    ii[0,:]=np.nan_to_num(it3, nan=-9999)
    ii[1,:]=np.nan_to_num(it5, nan=-9999)
    ii = np.mean(np.ma.array(ii,mask=ii<0),axis=0)
    
    cc = np.empty((2,len(it3)))
    cc[0,:]=np.nan_to_num(it8, nan=-9999)
    cc[1,:]=np.nan_to_num(it10, nan=-9999)
    cc = np.mean(np.ma.array(cc,mask=cc<0),axis=0)
    
    #for October and November different instrument is used, and no high channels are working, use 18kHz instead
    if date == '20201024' or date == '20191031':
        cc = np.empty((2,len(it3)))
        cc[0,:]=np.nan_to_num(it6, nan=-9999)
        cc[1,:]=np.nan_to_num(it7, nan=-9999)
        cc = np.mean(np.ma.array(cc,mask=cc<0),axis=0)
    
    it = cc/ii
    
    #mask = (it > 1) & (it < 1.7)
    #it = np.where(mask,1,it)
    
    chart = ax.scatter(xx,yy,c=it,s=5,cmap=plt.cm.plasma,vmin=.4,vmax=1)
    
    #get distance along the line
    dx = xx[1:]-xx[:-1]
    dy = yy[1:]-yy[:-1]
    dd = np.sqrt(dx**2+dy**2)
    distance.append(np.sum(np.ma.masked_invalid(dd))/1000)

if len(flist)>0:
    cb = plt.colorbar(chart, ax=ax, pad=.01)
    cb.set_label(label='Consolidation %',fontsize=20)
    cb.ax.tick_params(labelsize=20)

fig1.tight_layout(pad=0)
plt.show()
#fig1.savefig(outpath_plots+outname)

#plt.close(fig1)
print(np.sum(np.array(distance)))



            
