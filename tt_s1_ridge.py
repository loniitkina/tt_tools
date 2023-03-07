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


#2020-03-13 12:00:00,S1B_EW_GRDM_1SDH_20200313T114854_20200313T114954_020673_027304_FD59.SAFE
#2020-03-14 12:00:00,S1B_EW_GRDM_1SDH_20200314T122954_20200314T123054_020688_02737A_AE3C.SAFE
#2020-03-15 12:00:00,S1B_EW_GRDM_1SDH_20200315T113228_20200315T113328_020702_0273E8_513C.SAFE

tif='../data/S1/S1B_EW_GRDM_1SDH_20200313T114854_20200313T114954_020673_027304_FD59.SAFE/measurement/s1b-ew-grd-hh-20200313t114854-20200313t114954-020673-027304-001_warp_MOSAiC.tiff'
outname='S1B_20200313T114854_HH_map'
#refstation
#reference heading in Floenavi: 301.63560882616076
#2020-03-13 11:48:00,18.88062527803739,87.30794510596503,211.441695461282,3.533648020474092,0.7171529671308249
lon0=18.88062527803739
lat0=87.30794510596503
head0=211.441695461282

arr,rot_x,rot_y=proj_sat(tif,lon0,lat0,head0,spacing=1,band=1,alos=False)

#setup figure
fig1 = plt.figure(figsize=(20,10))

ax = fig1.add_subplot(111)
#do something about the PS (too high!)
#arr = np.where(arr>3.,3.,arr)
CS = plt.contourf(rot_x, rot_y, arr.T, 20)#,cmap=plt.cm.binary_r,alpha=.5)
#CS = plt.contourf(rot_x, rot_y, arr.T, 30, vmax=2., vmin=0,alpha=.5)

cb = plt.colorbar(CS)  # draw colorbar
cb.set_label(label='Intensity (dB)',fontsize=20)
#cb.set_label(label='Elevation (m)',fontsize=20)
cb.ax.tick_params(axis="y", labelsize=14)

#limit the region - overview
ax.set_xlim(-5000,5000)
ax.set_ylim(-5000,5000)



#prepare data for storing
data=arr.T.flatten()
rot_x=rot_x.flatten()
rot_y=rot_y.flatten()


#magnaprobe transects
#selected reference date: 20200116
inpath_table = '../data/MCS/MP/'
inpath_ridges1 = '../data/MCS/GEM2_thickness/01-ice-thickness/' #not re-calibrated, but converted to lines
inpath_ridges = '../data/MCS/GEM2_thickness/09-ridges-recal/'

#just first transects
flist = glob(inpath_ridges1+'*/mosaic-*20200108*ridgeFR1.csv')\
        +glob(inpath_ridges1+'*/mosaic-*20200110*ridgeFR2.csv')\
        +glob(inpath_ridges1+'*/mosaic-*20200131*ridgeFR3.csv')\
        +glob(inpath_ridges+'*/mosaic-*20200117*ridgeA1.csv')\
        +glob(inpath_ridges+'*/mosaic-*20200212*ridgeA2.csv')\
        +glob(inpath_ridges+'*/mosaic-*20200212*ridgeA3.csv')\
        +glob(inpath_table+'*/magna+gem2-transect-'+'*20200116*Nloop.csv')\
        +glob(inpath_table+'*/magna+gem2-transect-'+'*20191031*Nloop.csv')\
        +['../data/MCS/MP/recon/magna+gem220200108_recon.csv']

flist.sort()

for i in range(0,len(flist)):
    
    elev=[]
    elev_mean=[]
    elev_std=[]
    elev_n=[]
    fp=[]
    elev_mean2=[]
    elev_std2=[]
    elev_n2=[]
    
    fname = flist[i]
    print(fname)
    if fname==flist[-1]:
        loc='roads'
        date='20200108'
    else:
        date = fname.split('-')[-3].split('_')[0]
        loc = fname.split('_')[-1].split('.')[0]
        
    print(date)
    print(loc)
    
    #20200628 = lots of nans, has to be resolved beforewe can work with this data
    if date=='20200628' and loc=='ridgeA2':
        continue

    xx = getColumn(fname,3, delimiter=',')
    xx = np.array(xx,dtype=np.float)
    
    yy = getColumn(fname,4, delimiter=',')
    yy = np.array(yy,dtype=np.float)
    
    #Ice Thickness f5325Hz_hcp_i for ridge files and 18kHz for level ice transects
    it = getColumn(fname,8, delimiter=',')
    it = np.array(it,dtype=np.float)
    
    #adjust the individual profiles - use same adjustments as for the ALS!
    if loc=='roads':
        xx=xx+9
        yy=yy+1
    
    if loc=='ridgeFR1':
        osx=7
        osy=2
        if date=='20200108':
            xx=xx+osx
            yy=yy+osy
            #ax.scatter(xx,yy,c=it,s=20,cmap=plt.cm.Blues,vmin=0,vmax=5)
            
        if date=='20200119':
            xx=xx+osx
            yy=yy+3+osy
            
        if date=='20200221':
            xx=xx-2+osx
            yy=yy+5+osy
            
        if date=='20200305':
            xx=xx-3+osx
            yy=yy+30+osy
            #ax.scatter(xx,yy,c=it,s=20,cmap=plt.cm.Greens,vmin=0,vmax=5)
            
        xx_crest=xx[19]#DTC/crack at 17, crest at 19m, SIMBA at 22m, DTC at 27
        yy_crest=yy[19]
        
    if loc=='ridgeFR2':
        osx=12
        osy=3
        if date=='20200110':
            xx=xx+osx
            yy=yy+osy
            #ax.scatter(xx,yy,c=it,s=20,cmap=plt.cm.Greens,vmin=0,vmax=5)
            
        if date=='20200212':
            xx=xx-7+osx
            yy=yy-2+osy
            
        if date=='20200221':
            xx=xx-10+osx
            yy=yy+osy  
            
        xx_crest=xx[44]
        yy_crest=yy[44]
        
    if loc=='ridgeFR3':
        osx=9#5#9-1
        osy=-1#0
        if date=='20200131':
            xx=xx+osx
            yy=yy+osy
            
        xx_crest=xx[15]
        yy_crest=yy[15]   
        
    if loc=='ridgeA1':
        osx=0
        osy=-1
        crest=25
        if date=='20200117':
            xx=xx+osx
            yy=yy+osy
            #ax.scatter(xx,yy,c=it,s=50,cmap=plt.cm.Blues,vmin=0,vmax=5)
            #xx_crest=xx[crest]
            #yy_crest=yy[crest]
            #ax.plot(xx_crest,yy_crest,'s',c='purple')
            
        if date=='20200131': #18 m longer at the road? doesnt look like it from GEM track...
            xx=xx+5+osx
            yy=yy+2+osy
            
        if date=='20200228':
            xx=xx+12+osx
            yy=yy-2+osy
            
            
        if date=='20200410':
            xx=xx+osx
            yy=yy+62+osy 
            
        if date=='20200628':    #rotated
            xx=xx+1233+osx
            yy=yy+308+osy 
            #ax.scatter(xx,yy,c=it,s=50,cmap=plt.cm.Greens,vmin=0,vmax=5)
        xx_crest=xx[crest]
        yy_crest=yy[crest]  
        
    if loc=='ridgeA2':  #north (down of the main line on local coordinate maps)
        osx=5-2
        osy=0+2
        crest=33
        
        if date=='20200212':
            xx=xx+osx
            yy=yy+osy
            #ax.scatter(xx,yy,c=it,s=50,cmap=plt.cm.Blues,vmin=0,vmax=5)
            #xx_crest=xx[crest]
            #yy_crest=yy[crest]
            #ax.plot(xx_crest,yy_crest,'s',c='purple')

        if date=='20200228':
            xx=xx+osx+12
            yy=yy+osy

            
        if date=='20200410':
            xx=xx+osx
            yy=yy+62+osy 
            #ax.scatter(xx,yy,c=it,s=50,cmap=plt.cm.Greens,vmin=0,vmax=5)
            
        xx_crest=xx[crest]
        yy_crest=yy[crest]  
    
    if loc=='ridgeA3':  #south (up of the main line on local coordinate maps)
        osx=1
        osy=-5
        crest=33
        
        if date=='20200212':
            xx=xx+osx
            yy=yy+osy            
            #ax.scatter(xx,yy,c=it,s=50,cmap=plt.cm.Blues,vmin=0,vmax=5)
            #xx_crest=xx[crest]
            #yy_crest=yy[crest]
            #ax.plot(xx_crest,yy_crest,'s',c='purple')

        
        if date=='20200228':
            xx=xx+osx+12
            yy=yy+osy
        
        if date=='20200410':
            xx=xx+osx
            yy=yy+osy+62 
            
        if date=='20200628':    #rotated
            xx=xx+osx+1233
            yy=yy+osy+308 
            #ax.scatter(xx,yy,c=it,s=50,cmap=plt.cm.Greens,vmin=0,vmax=5)

        xx_crest=xx[crest]
        yy_crest=yy[crest] 
        
    if loc=='ridgeD':
        if date=='20200410':
            ax.scatter(xx,yy,c=it,s=20,cmap=plt.cm.Blues,vmin=0,vmax=5)
            
        if date=='20200416':
            xx=xx-15
            yy=yy
            
            
        if date=='20200424':
            xx=xx-14
            yy=yy-4
            
            
        if date=='20200430':   
            xx=xx-8
            yy=yy
            
            
        if date=='20200507':   
            xx=xx-10
            yy=yy-10   
            #ax.scatter(xx,yy,c=it,s=20,cmap=plt.cm.Greens,vmin=0,vmax=5)
            
    if loc=='Nloop':
        xx=xx+10
        yy=yy+0 
        
        if date=='20191031':
            xx=xx+0
            yy=yy-5
    
    ax.scatter(xx,yy,c=it,s=5,cmap=plt.cm.Reds,vmin=0,vmax=5)


plt.show()
#exit()
fig1.savefig(outpath_plots+outname,bbox_inches='tight')
plt.close(fig1)
    
#prepare data for CVL - 3DVIZ            
#transform all coordinates to lat,lon and store the data in text files
from pyproj import Proj, transform

#lat,lon projection
outProj = Proj(init='epsg:4326')

FloeNaviProj = Proj('+proj=stere +lat_0=%f +lon_0=%f +x_0=0 +y_0=0 +ellps=WGS84'%(80,0))

#transform to latlon-selected static position
lon_als,lat_als = transform(FloeNaviProj,outProj,rot_x,rot_y)

#write new csv file with all the ice mass balance variables
tt = [lon_als,lat_als,rot_x,rot_y,data]
table = list(zip(*tt))

outname = outpath+'S1_20200313T114854_intensityHH_latlon.txt'
print(outname)
with open(outname, 'wb') as f:
    #header
    f.write(b'Lon, Lat, X, Y, Intensity HH (dB)\n')
    np.savetxt(f, table, fmt="%s", delimiter=",")
