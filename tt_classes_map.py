import numpy as np
from osgeo import gdal, osr
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from datetime import datetime
from glob import glob
from tt_func import getColumn, proj_sat
import gc

outpath='../plots_gridded/'
out_type='classes'  #classes, snow, ice


#RS-2 scene for 31 Dec 2019, 03:35:02 UTC
tif='../data/RS-2_Wenkai/RS2_20191231_033502_0004_FQ20W_HHVVHVVH_SLC_783865_1107_32077288_HV.tif'
outname1='RS2_20191231_'
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


##The ALOS-2 image from 10 Nov 10:48:49 UTC.
#tif='../data/ALOS-2_Malin/ALOS2-HBQR1_1__A-ORBIT__ALOS2295171790-191110_Cal_ML.tif'
#outname='ALOS2_20191110_map.png'
#alos=True

##refstation for ALOS-2
##2019-11-10 10:48:00,116.11873002433686,85.82459083305169,295.83511127916154,1.4818942994101856,0.415055278122272
#lon0=116.11873002433686
#lat0=85.82459083305169
#head0=295.83511127916154

##TSX scene for 2019-11-14
##time stamp is 20191114T042434_20191114T042456
#tif='../data/TSX_Wenkai/TDX1_SAR__MGD_RE___SC_S_SRA_20191114T042434_20191114T042456.tif'
##ref station for TXS:
##2019-11-14 04:24:00,118.16217076435768,86.15982474551613,300.56654264271526,4.141477302772724,0.6866326529852491
#lon0=118.16217076435768
#lat0=86.15982474551613
#head0=300.56654264271526

##ship radar tifs
#tif='../data/ship_radar/S6_OUT0_20191231_035450.tif'
#outname='ship_radar_20191231.png'

##refstation (copied from RS-2 above)
#lon0=117.704953
#lat0=86.578373
#head0=302.2

#tif='../data/ship_radar/S6_OUT0_20200227_120030.tif'
#outname='ship_radar_20200227.png'

##refstation
###refstation for ALS (timestamp: 20200227), time: 11:43 to 13:20 (from leg 3 cruise report)
###2020-02-27 11:50:00,36.71483953107539,88.4101433020009,229.24061813074064,3.539174552604931,0.8996169107113513
#lon0=36.71483953107539
#lat0=88.4101433020009
#head0=229.24061813074064

#ALS tif from 21 Jan
#time: 20200121T103544-20200121T103614 to 20200121T121616-20200121T121646
#tif='../data/ALS/20200121_als_merged_grid-stere.tiff'
#outname='ALS_20200121_map.png'
#alos=False

##refstation
##2020-01-21 10:35:00,96.16950957480864,87.48817329565784,284.55644100627484,3.348816529475723,0.686339670008361
#lon0=96.16950957480864
#lat0=87.48817329565784
#head0=284.55644100627484



arr2,rot_x2,rot_y2=proj_sat(tif,lon0,lat0,head0,alos=alos,spacing=1,band=1,ps_pos=True)
#arr2,rot_x2,rot_y2=proj_sat(tif,lon0,lat0,head0,alos=alos,spacing=10,band=1,ps_pos=True)

#Wenkai masks no values as 999
arr2 = np.where(arr2==999,0,arr2)

#setup figure
fig1 = plt.figure(figsize=(35,15))
ax = fig1.add_subplot(111)


    
if alos:
    #ALOS-2
    CS1=ax.contourf(rot_x2, rot_y2, arr2, 25,cmap=plt.cm.binary_r, vmax=-5, vmin=-25)
    cb = plt.colorbar(CS1)  # draw colorbar
    cb.set_label(label='Intensity (dB)',fontsize=20)
else:
    ###for TSX and RS-2
    CS1=ax.contourf(rot_x2, rot_y2, arr2.T, 50,cmap=plt.cm.binary_r)
    #cb = plt.colorbar(CS1)  # draw colorbar
    #cb.set_label(label='Intensity (dB)',fontsize=20)
    
    ##for ALS
    ##do something about the PS (too high!)
    #arr = np.where(arr2>1.,1.,arr2)
    ##and some low points
    #arr = np.where(arr<0,0,arr)
    #CS2 = plt.contourf(rot_x2, rot_y2, arr.T, 30, vmax=1., vmin=0,cmap=plt.cm.binary_r,alpha=1)
    #cb = plt.colorbar(CS2)  # draw colorbar
    #cb.set_label(label='Elevation (m)',fontsize=20)
        
        
#transect paper
ax.set_xlim(-7000,2500)
ax.set_ylim(-1400,3700)

#larger ticks
ax.tick_params(axis="x", labelsize=18)
ax.tick_params(axis="y", labelsize=18)

#del arr, rot_x, rot_y
gc.collect()

#data produced by tt_profiles.py
fnames=['../data/classes_special20200107.csv',
        '../data/classes_special20200115.csv',
        '../data/classes_runway20200112.csv',
        '../data/classes_snow120200112.csv',
        '../data/classes_Sloop20200130.csv',
        '../data/classes_Nloop20200130.csv',
        '../data/classes_special20200123.csv',
        '../data/classes_special20200126.csv',
        '../data/classes_recon20200228.csv']

for fname in fnames:
    print(fname)

    xx = getColumn(fname,0, delimiter=',')
    xx = np.array(xx,dtype=np.float)

    yy = getColumn(fname,1, delimiter=',')
    yy = np.array(yy,dtype=np.float)

    cls = getColumn(fname,2, delimiter=',')
    cls = np.array(cls,dtype=np.float)

    si = getColumn(fname,3, delimiter=',')
    si = np.array(si,dtype=np.float)

    it = getColumn(fname,4, delimiter=',')
    it = np.array(it,dtype=np.float)

    if out_type=='classes':
        #roughness classes
        cmap = ListedColormap(["purple", "b", "c"])
        cs3=ax.scatter(xx,yy,c=cls,cmap=cmap,vmin=1,vmax=3)
        
        if fname==fnames[0]:
            cb = plt.colorbar(cs3,pad=.01)  # draw colorbar
            cb.set_label(label='Roughness class',fontsize=20)
            cb.ax.get_yaxis().set_ticks([])
            cb.ax.text(1.5,1.4,'level',rotation=90,fontsize=15)
            cb.ax.text(1.5,2,'rubble',rotation=90,fontsize=15)
            cb.ax.text(1.5,2.5,'ridges',rotation=90,fontsize=15)
    
    if out_type=='snow':
        #snow depth
        cs3=ax.scatter(xx,yy,c=si,vmin=0,vmax=.8)
        if fname==fnames[0]:
            cb = plt.colorbar(cs3,pad=.01)  # draw colorbar
            cb.set_label(label='Snow Depth (m)',fontsize=20)

    if out_type=='ice':
        #ice thickness
        cs3=ax.scatter(xx,yy,c=it,vmin=0,vmax=3)
        if fname==fnames[0]:
            cb = plt.colorbar(cs3,pad=.01)  # draw colorbar
            cb.set_label(label='Ice Thickness (m)',fontsize=20)
    
outname=outname1+out_type+'.png'    
fig1.savefig(outpath+outname,bbox_inches='tight')
