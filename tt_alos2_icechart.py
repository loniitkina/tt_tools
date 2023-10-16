import numpy as np
from osgeo import gdal, osr
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from datetime import datetime
from glob import glob
from tt_func import getColumn, proj_sat, logfit, running_stats
import gc
from scipy.signal import savgol_filter
from pyproj import Proj, transform
from mpl_toolkits.basemap import Basemap
import rasterio

#for debugging
#import ipdb; ipdb.set_trace()

#make your own Sentinel-1 tif images
#unzip
#gdal_translate ../data/CIRFA22/sat_images/S1A_EW_GRDM_1SDH_20220501T070432_20220501T070537_043014_0522C4_5982.SAFE/ ../data/CIRFA22/sat_images/S1A_EW_GRDM_1SDH_20220501T070432_20220501T070537_043014_0522C4_5982.tif
#gdalwarp ../data/CIRFA22/sat_images/S1A_EW_GRDM_1SDH_20220501T070432_20220501T070537_043014_0522C4_5982.tiff ../data/CIRFA22/sat_images/S1A_EW_GRDM_1SDH_20220501T070432_20220501T070537_043014_0522C4_5982w.tif
#to calibrate to intensities once could multiply the brightness values by 10*log10

#Station M
regs = 79.15; regn = 79.2
regw = -9.1; rege = -8.7

#ALOS-2 data (Truls)
inpath='../data/ALOS-2_Truls/processed/processed/**/'
resolution=5
sensor='ALOS-2'

#Sentinel-1 (Polona) - both bands in one file
inpath = '../data/CIRFA22/sat_images/**/S1A_EW_GRDM_1SDH_'
resolution=40   #in meters
sensor='Sentinel-1'

#Sentinel-1 (Johannes)
#inpath = '../data/CIRFA22/sat_images/S1A_EW_GRDM_1SDH_20220502T074527_20220502T074631_043029_05233F_7BC7w'
#resolution=80   #in meters
#sensor='Sentinel-1

##TSX (Wenkai)
#inpath = '../data/TSX_Wenkai/TSX_stationM_cut/TSX_stationM_cut/**/*_stationM'
#resolution=8
#sensor='TerraSAR-X'

#intensity_window=121; window_name='11x11';npixels=11
#intensity_window=81; window_name='9x9';npixels=9 #used in paper
#intensity_window=49; window_name='7x7';npixels=6 
#intensity_window=16; window_name='4x4';npixels=4 #4x4
#intensity_window=9; window_name='3x3';npixels=3 #3x3
#intensity_window=4; window_name='2x2';npixels=2 #2x2 
intensity_window=1; window_name='1x1';npixels=1 #no averaging

if npixels<3:
    polyorder = 2
else:
    polyorder = 3

#output
outpath='../plots_esa/'
outpath_data='../data/CIRFA22/sat_images/'
mapname='Roughness_map_'+sensor+'_'+str(resolution)+'_'
scatter_plot_name = 'Scatter_'+sensor+'_'+str(resolution)+'_'+window_name+'_'
#save the combined scatter data for further plots
scatter_file_name = outpath_data+'scatter_data_'+sensor+'_'+str(resolution)+'_'+window_name+'.csv'

fnames = glob(inpath+'*.tif')
print(fnames)

colors = iter(plt.cm.rainbow(np.linspace(0, 1, len(fnames)+1)))

#lat,lon projection
outProj = Proj(init='epsg:4326')

#transect data
inpath_transect='../data/CIRFA22/Landfast_M/'
rug_fn = glob(inpath_transect+'*-channel-thickness.csv')

tlons=[]
tlats=[]
tstd=[]

#get the transect data
for i in rug_fn:
    print(i)

    lons = getColumn(i,3, delimiter=',')
    lons = np.array(lons,dtype=np.float)     

    lats = getColumn(i,2, delimiter=',')
    lats = np.array(lats,dtype=np.float)

    it = getColumn(i,12, delimiter=',')
    it = np.array(it,dtype=np.float)#[1:]
    
    #get rid of those zeros
    lats = np.ma.array(lats, mask=lats==0)
    lons = np.ma.array(lons, mask=lats.mask).compressed()
    it = np.ma.array(it, mask=lats.mask).compressed()
    lats=lats.compressed()
    
    tlats.extend(lats)
    tlons.extend(lons)
    
    #WARNING:we have to make standard deviation/roughness from gridded it - here Q&D instead
    #running mean and variance
    nit=50
    itm,itv = running_stats(it,nit)
    std = np.sqrt(itv)
    tstd.extend(std)

tlats=np.array(tlats);tlons=np.array(tlons);tstd=np.array(tstd)

print(tlats.size)
print(tstd.size)

#start the general scatterplot
fig3 = plt.figure(figsize=(10,10))
ccx = fig3.add_subplot(111)
x_data=[]
y_data=[]

for fn in fnames:
    print(fn)
    
    ##Uncomment for preview
    #ds = gdal.Open(fn, gdal.GA_ReadOnly)
    #band = ds.GetRasterBand(1)  #band1=HV, band2=HH????
    #arr = band.ReadAsArray()
    #plt.imshow(arr)
    #plt.show()
    #exit()
    
    #collect data for this file/date/scene
    x_data_dt=[]
    y_data_dt=[]
    
    dt=fn.split('/')[-2].split('-')[-1]
    print('Date: ',dt)
    
    with rasterio.open(fn) as src:
        band1 = src.read(1)
        trs = src.transform
        height = band1.shape[0]
        width = band1.shape[1]
        cols, rows = np.meshgrid(np.arange(width), np.arange(height))
        xs, ys = rasterio.transform.xy(src.transform, rows, cols)
        
        # get CRS from dataset 
        ds = gdal.Open(fn, gdal.GA_ReadOnly) # Note GetRasterBand() takes band no. starting from 1 not 0
        crs = osr.SpatialReference()
        crs.ImportFromWkt(ds.GetProjectionRef())
        inProj=crs.ExportToProj4()
        print(inProj)
        
        xs= np.array(xs)
        ys = np.array(ys)
        lon,lat = transform(inProj,outProj,xs, ys)
        del xs,ys
        
        print('Longitude range: ',np.min(lon),np.max(lon))
        print('Latitude range: ',np.min(lat),np.max(lat))
    
    #missing values as 0
    if sensor=='TerraSAR-X':
        band1 = np.ma.array(band1,mask=band1==999)
    else:
        band1 = np.ma.array(band1,mask=band1==0)

    ##QD for Polonas S-1
    #band1 = 10*np.log10(band1)
    

    #setup map figure
    fig1 = plt.figure(figsize=(20,10))
    ax = fig1.add_subplot(111)
    
    # setup mercator map projection.
    map = Basemap(llcrnrlon=regw,llcrnrlat=regs,urcrnrlon=rege,urcrnrlat=regn,\
                rsphere=(6378137.00,6356752.3142),\
                resolution='i',projection='merc',\
                lat_0=-75.,lon_0=0.,lat_ts=75.)
    
    map.drawcoastlines()
    map.fillcontinents()
    map.drawparallels(np.arange(-90,90,1),labels=[1,1,0,1])
    map.drawmeridians(np.arange(-180,180,1),labels=[1,1,0,1])
    
    x,y = map(lon, lat)
    
    ##location looks shifted too... QD for Polona's S-1
    #x=x+250
    
    CS1=ax.pcolormesh(x,y,band1,cmap=plt.cm.binary_r)
    #CS1=ax.pcolor(x,y,band1,cmap=plt.cm.binary_r)
    cb = plt.colorbar(CS1)  # draw colorbar
    cb.set_label(label='Intensity (dB)',fontsize=20)

    #larger ticks
    ax.tick_params(axis="x", labelsize=18)
    ax.tick_params(axis="y", labelsize=18)
    
    #plot transect data on the map
    xx, yy = map(tlons, tlats)    
    print(xx.size)
    print(tstd.size)
    
    chart = ax.scatter(xx,yy,c=tstd,s=5,cmap=plt.cm.Blues,vmin=0,vmax=1)
    cb = plt.colorbar(chart, ax=ax, pad=.01)
    cb.set_label(label='Sea ice roughness (m)',fontsize=20)
    cb.ax.tick_params(labelsize=20)
    
    label=fn.split('/')[-1].split('.')[0]
    color = next(colors)
    
    fig1.savefig(outpath+mapname+label+'_'+dt+'.png',bbox_inches='tight')
    plt.close(fig1)
    #exit()
    
    #start collecting scatterplot data
    #subsample around station
    near_station_pix = ((lon > regw) *
            (lon < rege) * 
            (lat > regs) * 
            (lat < regn))
    # that will return lon,lat as vectors, not as grids   
    lon, lat, band1 = lon[near_station_pix] , lat[near_station_pix], band1[near_station_pix]
    #project again to figure/map coordinates
    x,y = map(lon, lat)
    
    ##location looks shifted too... QD for Polona's S-1
    #x=x+250
    
    #mask arrays
    data=band1.T; del band1
    x=np.ma.array(x,mask=data.mask).compressed()
    y=np.ma.array(y,mask=data.mask).compressed()
    data=data.compressed()
    
    #get smooting window size/sampling interval - here we use X pixel size: ~positioning error + ~roughness feature size
    #how many measurements in one/three TSX pixel size, this depends on MP sampling spacing (1-3m)
    #get mean distance between fixed date MP points
    dx = xx[1:]-xx[:-1]
    dy = yy[1:]-yy[:-1]
    md = np.mean(np.sqrt(dx**2+dy**2))

    window = int(npixels*resolution/md); print('window: ',window)
    #window has to be an odd number
    if np.mod(window,2)==0: window=window+1; print('odd number window: ',window)
    try:
        tstdm = savgol_filter(tstd, window, polyorder)
    except:
        continue    #sometimes there is not enough data to apply the smoothing filter
    
    #take a value for every pixel/every 3 pixels and every roughness feature scale (24 m is again a good first guess)
    #this depends on the measurement spacing
    xxm = xx[::window]
    yym = yy[::window]
    tstdm = tstdm[::window]        
    print('Transect points: ',xxm.shape)
    
    hh_mean=[]
    for i in range(0,len(xxm)):
        dx = xxm[i]-x
        dy = yym[i]-y
        d = np.sqrt(dx**2+dy**2)
        
        ##take average a window (closest pixels)
        hh_mean.append(np.mean(data[np.argsort(np.abs(d))[:intensity_window]]))
    
    print('Pixel means: ',hh_mean)
    
    #plot roughness vs mean window intensity
    fig2 = plt.figure(figsize=(10,10))
    cx = fig2.add_subplot(111)
    
    cx.scatter(tstdm,hh_mean,c=color,label=label)
    
    #and same on the combined plot
    ccx.scatter(tstdm,hh_mean,c=color,alpha=.5,label=label)
    
    #store the data points
    x_data_dt.extend(tstdm)
    y_data_dt.extend(hh_mean)
    x_data.extend(tstdm)
    y_data.extend(hh_mean)
    
    del hh_mean,tstdm,xxm,yym,dx,dy,d

    #curve fit to individual date/scene
    x_data_dt = np.array(x_data_dt,dtype=np.float).flatten()  #has nans
    y_data_dt = np.array(y_data_dt,dtype=np.float).flatten()
    x_data_dt = np.ma.masked_invalid(x_data_dt)
    y_data_dt = np.ma.array(y_data_dt,mask=x_data_dt.mask).compressed()
    x_data_dt = x_data_dt.compressed()

    try:
        x_model,y_model,RMSE,Rsquared = logfit(x_data_dt,y_data_dt)
        cx.plot(x_model,y_model)
        cx.text(.9, .2, 'R^2: '+str(np.round(Rsquared,2)), ha="center", va="center", size=20, transform=cx.transAxes)
        cx.text(.9, .15, 'RMSE: '+str(np.round(RMSE,2)), ha="center", va="center", size=20, transform=cx.transAxes)
        
        cx.set_xlabel('Roughness (m)', fontsize=20) # X axis data label
        cx.set_ylabel('Intensity (dB)', fontsize=20) # Y axis data label
        cx.tick_params(axis="x", labelsize=18)
        cx.tick_params(axis="y", labelsize=18)

        #cx.set_xlim(-.1,3.1)
        #cx.set_ylim(-23,0)
        cx.legend(fontsize=20)
        fig2.savefig(outpath+scatter_plot_name+label+'_'+dt,bbox_inches='tight')
        plt.close(fig2)
    except:
        continue #some large windows wont have enough data, too big scatter
        
#store data
x_data = np.array(x_data,dtype=np.float).flatten()  #has nans
y_data = np.array(y_data,dtype=np.float).flatten()
x_data = np.ma.masked_invalid(x_data)
y_data = np.ma.array(y_data,mask=x_data.mask).compressed()
x_data = x_data.compressed()

tt = [x_data,y_data]
table = list(zip(*tt))

with open(scatter_file_name, 'wb') as f:
    #header
    f.write(b'roughness from transect, intensity (dB)\n')
    np.savetxt(f, table, fmt="%s", delimiter=",")

## curve fit to whole period/winter/all scenes
#try:
    #x_model,y_model,RMSE,Rsquared = logfit(x_data,y_data)
    #ccx.plot(x_model, y_model)
    
    ##add some text
    #ccx.text(2.5, -20, 'R^2: '+str(np.round(Rsquared,2)), ha="center", va="center", size=25)
    #ccx.text(2.5, -22, 'RMSE: '+str(np.round(RMSE,2)), ha="center", va="center", size=25)
    
    #ccx.set_xlabel('Roughness (m)') # X axis data label
    #ccx.set_ylabel('Intensity (dB)') # Y axis data label

    ##ccx.set_xlim(-.1,3.1)
    ##ccx.set_ylim(-23,0)
    #ccx.legend(fontsize=20)
    #fig3.savefig(outpath+scatter_plot_name+window_name,bbox_inches='tight')
    #plt.close(fig3) 
    
#except:
    #print('No fit possible')
    


        
#Some relevation/heresy:
#X-band, the shortest of the SARs can only detect geometric scattering in thick ice. No volumetric scattering. The thick ice is only smooth-rough-roughest.
#There the brightness can be explained completely by the surface roughness. This will become evident when the ALS images will become available.
#The leads are sometimes smooth, sometimes rough and sometimes smooth with volumetric scattering-frost flowers. This is why we will never know what is what there.
#salt in leads is crucial. Surface hoar on snow (pure ice) has no effect on the signal.
#Do we have sea ice core bubble content from FYI and SYI published? Was bubble content similar? I expect there was very little bubbles. Refer to Rostosky paper. Was there really a large difference at N-ICE?
#All this means just re-labeling of the classes, no difference for the method. Now we get level ice, deformed ice and very deformed ice, bright and dark leads

#Co-location of airborne data and SAR data is a known problem. Airborne data is voluminus, but diferential deformation (not just drift!) causes problems and disables direct comparisions. Even at very short time differences (less than 1 hour!).
#Here we try to overcome this problem by using a small amount of well described and analysed ground data that were first automatically drift-corected and (in case of deformation only!) then manual laterally shifted to correspond to the positions of recognised geometry. This is done for the area of about 1x1km - CO. There we have measurements and visual observations of observers moving on the ground on a weekly basis.
#ALS data even when completly dirft corrected, will contain a lot of deformation inside the 6x6km area and 1to1 comparision will remain challenging...
#Only good alternative is landfast ice...
#The roughness we use is not surface roughness, but also bottom roughness measure - SAR only measures surface roughness - fat cloud 

#Because the relationship between the roughness and intensity is a logarithmic function, the high roughness classes are hard to distinguish. Or this function is logarithmic bacause of speckle problem - saturation of pixel signal...
#in X-band this saturation starts happening after 0.5 roughness - that is above the level of ridges (Itkin et al, transect paper). This band is good for detecting all kinds of roughness. C- and L-band are likely getting saturated later, at higher roughnesses.
#The data sample is not big enough to say how this function depends on the IA...
#Leads with frost flowers are not included into this graph

#MAIN MESSAGE - this can be used in Methods/Introduction. The relationship gives clear indications, but is not good enough to use it for roughness estimations. 
#Does is imprprove with IA correction? No - no influence?
#It is only good enough to use it for classification that takes into acocunt IA and takes some context information into account - and that also just with the help of texture.
#This means we dont need a complicated classification: we can just estimate roughness from X-band SAR and then distribute the snow over it...
