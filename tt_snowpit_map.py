import numpy as np
from osgeo import gdal, osr
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from datetime import datetime
from glob import glob
from tt_func import getColumn, proj_sat
import gc


#reference heading in Floenavi: 301.63560882616076
#on 20/2/2020: 266.5130272362738 >> 40 deg difference!

outpath='../plots_gridded/'

#RS-2 scene for 31 Dec 2019, 03:35:02 UTC
tif='../data/RS-2_Wenkai/RS2_20191231_033502_0004_FQ20W_HHVVHVVH_SLC_783865_1107_32077288_HV.tif'
outname='RS2_20191231_map_snowpits_selection.png'
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

arr2,rot_x2,rot_y2=proj_sat(tif,lon0,lat0,head0,alos=alos,spacing=1,band=1,ps_pos=True)


#Wenkai masks no values as 999
arr2 = np.where(arr2==999,0,arr2)

#setup figure
fig1 = plt.figure(figsize=(20,12))
ax = fig1.add_subplot(111)

###for TSX and RS-2
CS1=ax.contourf(rot_x2, rot_y2, arr2.T, 50,cmap=plt.cm.binary_r)
cb = plt.colorbar(CS1)  # draw colorbar
cb.set_label(label='Intensity (dB)',fontsize=20)

#limit the region
ax.set_xlim(-2000,2000)
ax.set_ylim(-1500,1500)

#larger ticks
ax.tick_params(axis="x", labelsize=18)
ax.tick_params(axis="y", labelsize=18)

#del arr, rot_x, rot_y
gc.collect()


#plot some transect tracks from CO1
inpath = '../data/MCS/GEM2_thickness/01-ice-thickness/'
flist = glob(inpath+'*PS122-[2]?*/mosaic-*-*-gem2-*-track-icecs-xy.csv')
flist.sort()

#magnaprobe transects
inpath_table = '../data/MCS/MP/'
flist = glob(inpath_table+'*/magna+gem2-transect-'+'*.csv')
flist.sort()

for i in range(0,len(flist)):
    
    fname = flist[i]
    print(fname)
    date = fname.split('-')[-3].split('_')[0]
    print(date)
    loc = fname.split('_')[-1].split('.')[0]
    print(loc)
    #exit()

    xx = getColumn(fname,3, delimiter=',')
    xx = np.array(xx,dtype=np.float)
    
    yy = getColumn(fname,4, delimiter=',')
    yy = np.array(yy,dtype=np.float)
    
    #GEM-2 files contain nans and zeros
    xx = np.ma.masked_invalid(xx).compressed()
    yy = np.ma.masked_invalid(yy).compressed()
    
    xx = np.ma.array(xx,mask=xx==0).compressed()
    yy = np.ma.array(yy,mask=yy==0).compressed()
    
    #plot tracks
    #Sloop, Nloop
    if date=='20200116':
        if loc=='Sloop':
            ax.plot(xx,yy,'o',ms=5,c='purple')
        if loc=='Nloop':
            ax.plot(xx,yy,'o',ms=5,c='salmon')
    ##Nloop start
    #if date=='20191031' and loc=='Nloop':
        #ax.plot(xx,yy,'o',ms=2,c='salmon')
    #snow1, runway
    if date=='20200112':
        if loc=='snow1':
            ax.plot(xx,yy,'o',ms=5,c='gold')
        if loc=='runway':
            ax.plot(xx,yy,'o',ms=5,c='pink')
    #long
    if date=='20200123':
        ax.plot(xx,yy,'o',ms=5,c='c')
    #event
    if date=='20200126' and loc=='special':
        ax.plot(xx,yy,'o',ms=5,c='darkred')
    #dark side FYI
    if date=='20200107' and loc=='special':
        ax.plot(xx,yy,'o',ms=5,c='darkkhaki')
    #dark side SYI
    if date=='20200115' and loc=='special':
        ax.plot(xx,yy,'o',ms=5,c='b')
    ##dranitsyn lead
    #if date=='20200226':
        #ax.plot(xx,yy,'o',ms=5,label='dranitsyn',c='y')
    ##RS site, leg 3
    #if date=='20200430':
        #if loc=='special':
            #ax.plot(xx,yy,'o',ms=5,label='RS site',c='darkkhaki')
        
    #Allies Ridge
    if date=='20200228':
        if loc=='ridgeA1':
            ax.plot(xx,yy,'o',ms=5,c='limegreen')
        else:
            ax.plot(xx,yy,'o',ms=5,c='limegreen')
    #Fort Ridge
    if date=='20200221':
        ax.plot(xx,yy,'o',ms=5,c='limegreen')
    if date=='20200131' and loc=='ridgeFR3':
        ax.plot(xx,yy,'o',ms=5,c='limegreen')
    #Davids Ridge
    if date=='20200424' and loc=='ridgeD':
        ax.plot(xx,yy,'o',ms=5,c='limegreen')
    if date=='20200424' and loc=='ridgeE':
        ax.plot(xx,yy,'o',ms=5,c='limegreen')
        
    del xx,yy
            
#snow pit locations
fnames = glob('../data/snowpits_wagner/swe_smpdensity_leg1_leg3_archive/metdata_and_plot_qc/swe_smp_k2020_*.csv')
selection = ['snow1-A1','snow1-A3','snow1-A5','snow1-A5*','runway1','RS-transect-north']

colors = plt.cm.jet(np.linspace(0, 1, len(fnames)))

for i in range(0,len(fnames)):
    fname = fnames[i]
    snowpit = fname.split('_')[-1].split('.csv')[0]
    print(snowpit)
    
    if snowpit in selection:
        
        x = getColumn(fname,6)
        x = np.array(x,dtype=np.float)
        y = getColumn(fname,7)
        y = np.array(y,dtype=np.float)

        ax.plot(x,y,'x',ms=5,c=colors[i],label=snowpit)

ax.legend()

fig1.savefig(outpath+outname,bbox_inches='tight')
