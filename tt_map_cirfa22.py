import numpy as np
from osgeo import gdal, osr
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from datetime import datetime
from glob import glob
from tt_func import getColumn, proj_sat, logfit
import gc
from scipy.signal import savgol_filter
from pyproj import Proj, transform
from pyresample.geometry import AreaDefinition
import pyresample as pr
from mpl_toolkits.basemap import Basemap
import rasterio


#for debugging
#import ipdb; ipdb.set_trace()

#reference heading in Floenavi: 301.63560882616076

inpath='../data/iceEYE/'
inpath_cls='../data/'
outpath='../plots_cirfa22/'

#station S
tran_fn1 = sorted(glob('../data/CIRFA22/Landfast_S/transect-CIRFA22-*-thickness.csv'))
tran_fn2 = sorted(glob('../data/CIRFA22/Landfast_S/transect-CIRFA22-*-track.csv'))

mp_fn1 = sorted(glob('../data/CIRFA22/Landfast_S/magnaprobe-*.dat'))
mp_fn2 = sorted(glob('../data/CIRFA22/Landfast_S/magnaprobe-*track.csv'))

smp_coords=glob('../../../CIRFA_cruise/data/CIRFA_landfast_S/**/SMP/**/SMP_coordinates.csv')

#IMB deployment map
outname='Transects_Landfast_S.png'
regs = 78.6; regn = 78.75
regw = -12.5; rege = -11.5
##ice station map
#outname='Transects_Landfast_S_station_snow.png'
#regs = 78.675; regn = 78.685
#regw = -12.21; rege = -12.17

dt='20220427'
dt='20220426'
fn1 = glob(inpath+'*'+dt+'*.tif')[0]

##station M
#tran_fn1 = sorted(glob('../data/CIRFA22/Landfast_M/transect-CIRFA22-*-thickness.csv'))
#tran_fn2 = sorted(glob('../data/CIRFA22/Landfast_M/transect-CIRFA22-*-track.csv'))
#fn1 = '../data/CIRFA22/sat_images/middle_fast_ice_S2_20220427_epsg3996.tif'

#mp_fn1 = sorted(glob('../data/CIRFA22/Landfast_M/magnaprobe-*.dat'))
#mp_fn2 = sorted(glob('../data/CIRFA22/Landfast_M/magnaprobe-*track.csv'))

#smp_coords=glob('../../../CIRFA_cruise/data/CIRFA_landfast_M/SMP/**/SMP_coordinates.csv')

##IMB deployment map
#outname='Transects_Landfast_M.png'
#regs = 79.15; regn = 79.2
#regw = -9.1; rege = -8.7

##ice station map
#outname='Transects_Landfast_M_station_snow.png'
#regs = 79.168; regn = 79.172
#regw = -8.91; rege = -8.895

##station N
#tran_fn1 = sorted(glob('../data/CIRFA22/Landfast_N/transect-CIRFA22-*-thickness.csv'))
#tran_fn2 = sorted(glob('../data/CIRFA22/Landfast_N/transect-CIRFA22-*-track.csv'))

#fn1 = '../data/CIRFA22/sat_images/s1_mosaic_belgica_20220503_HV_epsg3996_LR.tif'
#fn1 = '../data/CIRFA22/sat_images/S1_test.tif'

##transect map
#outname='Transects_Landfast_N.png'
#regs = 79.85; regn = 79.95
#regw = -9.5; rege = -8.5

##station map
#outname='Transects_Landfast_N_station.png'
#regs = 79.871; regn = 79.875
#regw = -8.82; rege = -8.8

print(tran_fn1)



print(fn1)


fig, ax = plt.subplots(1,1,figsize=(25,15))

#get the geotiff on the map
with rasterio.open(fn1) as src:
    band1 = src.read(1)
    trs = src.transform
    height = band1.shape[0]
    width = band1.shape[1]
    cols, rows = np.meshgrid(np.arange(width), np.arange(height))
    xs, ys = rasterio.transform.xy(src.transform, rows, cols)
    
    #transformer = Transformer.from_crs(src.crs, "EPSG:4326", src.crs)
    # get CRS from dataset 
    ds = gdal.Open(fn1, gdal.GA_ReadOnly) # Note GetRasterBand() takes band no. starting from 1 not 0
    crs = osr.SpatialReference()
    crs.ImportFromWkt(ds.GetProjectionRef())
    inProj=crs.ExportToProj4()
    
    print(inProj)
    exit()

    #lat,lon projection
    outProj = Proj(init='epsg:4326')


    lons= np.array(xs)
    lats = np.array(ys)
    #lon, lat = transformer.transform(lons,lats)
    lon,lat = transform(inProj,outProj,lons, lats)

    # setup mercator map projection.
    map = Basemap(llcrnrlon=regw,llcrnrlat=regs,urcrnrlon=rege,urcrnrlat=regn,\
                rsphere=(6378137.00,6356752.3142),\
                resolution='i',projection='merc',\
                lat_0=-75.,lon_0=0.,lat_ts=75.)
    
    #map.pcolormesh(lat,lon, band1,latlon=True,vmin=50,vmax=100)
    
    x,y = map(lon, lat)
    ax.pcolormesh(x,y,band1)

    map.drawcoastlines()
    map.fillcontinents()
    map.drawparallels(np.arange(-90,90,1),labels=[1,1,0,1])

    map.drawmeridians(np.arange(-180,180,1),labels=[1,1,0,1])

#plot some transect data
for i in range(0,len(tran_fn1)):
    print(tran_fn1[i])
    print(tran_fn2[i])

    lons = getColumn(tran_fn2[i],1, delimiter=',')
    lons = np.array(lons,dtype=np.float)     

    lats = getColumn(tran_fn2[i],2, delimiter=',')
    lats = np.array(lats,dtype=np.float)

    it = getColumn(tran_fn1[i],12, delimiter=',')
    it = np.array(it,dtype=np.float)[1:]
    
    #get rid of those zeros
    lats = np.ma.array(lats, mask=lats==0)
    lons = np.ma.array(lons, mask=lats.mask).compressed()
    it = np.ma.array(it, mask=lats.mask).compressed()
    lats=lats.compressed()
    
    print(lats,lons)
    
    #plot
    xx, yy = map(lons, lats)    
    chart = ax.scatter(xx,yy,c=it,s=5,cmap=plt.cm.rainbow,vmin=0.8,vmax=1.2)
    
            
cb = plt.colorbar(chart, ax=ax, pad=.01)
cb.set_label(label='Sea ice thickness (m)',fontsize=20)
cb.ax.tick_params(labelsize=20)

##snow depth transects 
#for i in range(0,len(mp_fn1)):
    #print(mp_fn1[i])
    #print(mp_fn2[i])

    #lons = getColumn(mp_fn2[i],1, delimiter=',')
    #lons = np.array(lons,dtype=np.float)     

    #lats = getColumn(mp_fn2[i],2, delimiter=',')
    #lats = np.array(lats,dtype=np.float)

    #sd = getColumn(mp_fn1[i],3, delimiter=',', skipheader=4)
    #sd = np.array(sd,dtype=np.float)[1:]/100
    
    ##get rid of those zeros
    #lats = np.ma.array(lats, mask=lats==0)
    #lons = np.ma.array(lons, mask=lats.mask).compressed()
    #sd = np.ma.array(sd, mask=lats.mask).compressed()
    #lats=lats.compressed()
    
    ##print(lats,lons)
    
    ##plot
    #xx, yy = map(lons, lats)    
    #chart = ax.scatter(xx,yy,c=sd,s=5,cmap=plt.cm.Reds,vmin=0,vmax=1)
    
            
#cb = plt.colorbar(chart, ax=ax, pad=.01)
#cb.set_label(label='Snow depth (m)',fontsize=20)
#cb.ax.tick_params(labelsize=20)

##SMP coordinates
#for fn in smp_coords:
    #print(fn)
    
    #lons = getColumn(fn,0, delimiter=',')
    #lons = np.array(lons,dtype=np.float)     

    #lats = getColumn(fn,1, delimiter=',')
    #lats = np.array(lats,dtype=np.float)
    
    #xx, yy = map(lons, lats)
    #ax.plot(xx,yy,'x',c='b')

fig.savefig(outpath+outname,bbox_inches='tight')
plt.close(fig)
#plt.show()
