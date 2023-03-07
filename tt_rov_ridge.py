import numpy as np
from osgeo import gdal, osr
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from datetime import datetime
from glob import glob
from tt_func import getColumn, proj_rov
import gc

outpath='../data/ridges/'
outpath_plots='../plots_ridges/'

##ROV multibeam data
#tif='../data/MOSAiC_ROV_MB_PANGEA/PS122_2_19_27_20200107_ROV_MULTIBEAM_v1_raster.tiff'
#outname='ROV_multibeam_transects_overview.png'
#version='_ROV_20200107'
##metadata:../data/MOSAiC_ROV_MB_PANGEA/MOSAiC_BEAST_Sea-ice_draft.tab 
##start time:2020-01-07T06:45:00
##end time:2020-01-07T13:14:00
##refstation
##reference heading in Floenavi: 301.63560882616076
##2020-01-07 06:45:00,114.92158700136054,87.12092944920997,298.4116307624573,3.8752930801668546,1.6389446771711977
##lon0=114.92158700136054
##lat0=87.12092944920997
##head0=298.4116307624573

#lon0=114.92158700136054
#lat0=87.12092944920997
#head0=298.68350213431756
#head0=head0-63   #adjusted manually for rotation
#lon_origin=114.933499
#lat_origin=87.121199
#x_offset=905+10
#y_offset=-670-5

tif='../data/MOSAiC_ROV_MB_PANGEA/PS122_2_22_45_20200128_ROV_MULTIBEAM_v1_raster.tiff'
outname='ROV_multibeam_transects_FR.png'
version='_ROV_20200128'
version='_ROV_20200128_match'
#metadata:../data/MOSAiC_ROV_MB_PANGEA/MOSAiC_BEAST_Sea-ice_draft.tab 
##start time:2020-01-28T06:48:00
##end time:2020-01-28T10:56:00
##refstation
##reference heading in Floenavi: 301.63560882616076
#2020-01-28 06:48:00,95.81595474392334,87.45167110623571,287.10251418256775,4.633817530252664,0.9073634721915533

lon0=95.81595474392334
lat0=87.45167110623571
head0=287.10251418256775
head0=head0-40-6+5   #adjusted manually for rotation
lon_origin=95.828327
lat_origin=87.452089
x_offset=727+20-10-5+9+5-2
y_offset=-520+80+5-40-10+5-7+40+4



arr,rot_x,rot_y=proj_rov(tif,lon0,lat0,head0,lon_origin,lat_origin)

#manual shift of the reprojected mercator projection
rot_x = rot_x+x_offset
rot_y = rot_y+y_offset

#


#setup figure
fig1 = plt.figure(figsize=(20,10))

ax = fig1.add_subplot(111)
arr = np.where(arr>10.,10.,arr)
CS = plt.contourf(rot_x, rot_y, arr.T, 30, vmax=7., vmin=0,alpha=.5)#,cmap=plt.cm.Reds)

#plt.scatter(rot_x, rot_y)


cb = plt.colorbar(CS)  # draw colorbar
#cb.set_label(label='Intensity (dB)',fontsize=20)
cb.set_label(label='Draft (m)',fontsize=20)
cb.ax.tick_params(axis="y", labelsize=14)

##limit the region - overview
#ax.set_xlim(150,900)
#ax.set_ylim(-600,-50)

#limit the region - Fort Ridge
ax.set_xlim(200,350)
ax.set_ylim(-500,-350)

#prepare data for search
data=arr.T.flatten()
rot_x=rot_x.flatten()
rot_y=rot_y.flatten()

#magnaprobe transects
#selected reference date: 20200116
inpath_table = '../data/MCS/MP/'
inpath_ridges1 = '../data/MCS/GEM2_thickness/01-ice-thickness/' #not re-calibrated, but converted to lines
inpath_ridges = '../data/MCS/GEM2_thickness/09-ridges-recal/'
#flist = glob(inpath_ridges1+'*/mosaic-*-gem2-*ridgeFR[1-3]*.csv')\
        #+glob(inpath_ridges+'*/mosaic-*-gem2-*ridgeA[1-3]*.csv')\
        #+glob(inpath_table+'*/magna+gem2-transect-'+'*ridgeD.csv')\
        #+glob(inpath_table+'*/magna+gem2-transect-'+'*20200116*Nloop.csv')\
        #+glob(inpath_table+'*/magna+gem2-transect-'+'*20191031*Nloop.csv')
        
#flist = glob(inpath_table+'*/magna+gem2-transect-'+'*ridge*.csv')

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
    #adjust the individual profiles - use same adjustments as for the ALS!
    if loc=='roads':
        xx=xx+9#6+1+5-3
        yy=yy+1#-7+3+5
    
    if loc=='ridgeFR1':
        osx=7#4+1+2
        osy=2#-1+2+1
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
        osx=12#8+5-1-2+2#+4#13 #or try osx=15,osy=0
        osy=5+3-5#4+3+1+1-4#+4
        
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
        osx=0
        osy=0
        if date=='20200228':
            xx=xx+12+osx
            yy=yy-2+osy
            #ax.scatter(xx,yy,c=it,s=50,cmap=plt.cm.Blues,vmin=0,vmax=5)
            
        if date=='20200410':
            xx=xx+osx
            yy=yy+62+osy 
            #ax.scatter(xx,yy,c=it,s=50,cmap=plt.cm.Greens,vmin=0,vmax=5)
            
        xx_crest=xx[32]
        yy_crest=yy[32]  
    
    if loc=='ridgeA3':  #south (up of the main line on local coordinate maps)
        osx=-2
        osy=0
        if date=='20200228':
            xx=xx+12
            yy=yy-2
            #ax.scatter(xx,yy,c=it,s=50,cmap=plt.cm.Blues,vmin=0,vmax=5)
        
        if date=='20200410':
            xx=xx
            yy=yy+62 
            
        if date=='20200628':    #rotated
            xx=xx+1233
            yy=yy+308 
            #ax.scatter(xx,yy,c=it,s=50,cmap=plt.cm.Greens,vmin=0,vmax=5)

        xx_crest=xx[33]
        yy_crest=yy[33] 
        
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
            
            
        #save these data for 3dVIZ
        from pyproj import Proj, transform

        #lat,lon projection
        outProj = Proj(init='epsg:4326')

        FloeNaviProj = Proj('+proj=stere +lat_0=%f +lon_0=%f +x_0=0 +y_0=0 +ellps=WGS84'%(80,0))

        #transform to latlon-selected static position
        lon_als,lat_als = transform(FloeNaviProj,outProj,xx,yy)

        #write new csv file with all the ice mass balance variables
        tt = [lon_als,lat_als,xx,yy,data]
        table = list(zip(*tt))

        outname1 = outpath+'transect_latlon.txt'
        print(outname1)
        with open(outname1, 'wb') as f:
            #header
            f.write(b'Lon, Lat, X, Y, Total thickness (m)\n')
            np.savetxt(f, table, fmt="%s", delimiter=",")

    ax.scatter(xx,yy,c=it,s=5,cmap=plt.cm.Reds,vmin=0,vmax=5)

    if loc=='ridgeFR1' or loc=='ridgeFR2' or loc=='ridgeFR3':
        #mark crest
        ax.plot(xx_crest,yy_crest,'X',c='gold')

        #get closest values in MB array
        for j in range(0,len(xx)):
            dx = xx[j]-rot_x
            dy = yy[j]-rot_y
            d = np.sqrt(dx**2+dy**2)
        
            #closest in MB array
            elev.append(data[np.argmin(np.abs(d))])
            
            #make means for the GEM-2 footprint (also standard deviation and sample size)
            #footprint10=10 
            footprint2=.5   #radius  (for 1 meter radius we get ~15 values in HR scan)
            #footprint = it[j]*4
            footprint = it[j]*2
            sample = data[d<footprint]
            sample2 = data[d<footprint2]
            elev_mean.append(np.mean(sample))
            elev_std.append(np.std(sample))
            elev_n.append(sample.size)
            fp.append(footprint)
            elev_mean2.append(np.mean(sample2))
            elev_std2.append(np.std(sample2))
            elev_n2.append(sample2.size)

        print(fp)
        
        #write file
        tt = [xx,yy,elev,elev_mean,elev_std,elev_n,fp,elev_mean2,elev_std2,elev_n2]
        table = list(zip(*tt))

        file_name=outpath+fname.split('/')[-1].split('.csv')[0]+version+'.csv'
        print(file_name)
        with open(file_name, 'wb') as f:
            #header
            f.write(b'x,y,nearest MB draft (m), mean MB draft (m), std MB draft (m), sample size, footprint=4xtt (m), mean MB draft-fp=2 (m), std MB draft-fp=2 (m), sample size-fp=2\n')
            np.savetxt(f, table, fmt="%s", delimiter=",")

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

outname = outpath+'ROV_draft_HR_latlon.txt'
print(outname)
with open(outname, 'wb') as f:
    #header
    f.write(b'Lon, Lat, X, Y, Draft (m)\n')
    np.savetxt(f, table, fmt="%s", delimiter=",")

        

            
