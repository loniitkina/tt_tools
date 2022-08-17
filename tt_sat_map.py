import numpy as np
from osgeo import gdal, osr
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from datetime import datetime
from glob import glob
from tt_func import getColumn, proj_sat
import gc


#reference heading in Floenavi: 301.63560882616076

#do you want just subset map (Sloop)?
subset=False
#subset=True

outpath='../plots_gridded/'
outpath='../plots_revision/'










if subset:
    
 
    ##ALS tif from 27 Feb
    #tif='../data/ALS/20200227_als_merged_grid-stere.tiff'
    #outname='ALS_20200227.png'
    #outname='ALS_20200227_legend.png'
    #outname='ALS_20200227_legend_paper.png'
    #outname='ALS_20200227_legend_Sloop.png'
    #outname='ALS_20200227_legend_Sloop_RS-2.png'
    ##plt.imshow(arr)
    ##plt.show()

    ##refstation for ALS (timestamp: 20200227), time: 11:43 to 13:20 (from leg 3 cruise report)
    ##2020-02-27 11:50:00,36.71483953107539,88.4101433020009,229.24061813074064,3.539174552604931,0.8996169107113513
    #lon0=36.71483953107539
    #lat0=88.4101433020009
    #head0=229.24061813074064

    #ALS tif from 21 Jan
    #time: 20200121T103544-20200121T103614 to 20200121T121616-20200121T121646
    tif='../data/ALS/20200121_als_merged_grid-stere-all.tiff'
    tif='../data/ALS/20200121_als_merged_grid-stere.tiff'
    outname='ALS_20200121.png'
    outname='ALS_20200121_all.png'
    #outname='ALS_20200121_Sloop.png'

    #refstation
    #2020-01-21 10:35:00,96.16950957480864,87.48817329565784,284.55644100627484,3.348816529475723,0.686339670008361
    lon0=96.16950957480864
    lat0=87.48817329565784
    head0=284.55644100627484

    

    #get all arrays to plot the background
    arr,rot_x,rot_y=proj_sat(tif,lon0,lat0,head0,spacing=4,band=1,alos=False)

#RS-2 scene
#cropped from a composite of RS2_20191110_032238_0004_FQ16_HHVVHVVH_SLC_770940_0385_31250903 and RS2_20191110_032241_0005_FQ16_HHVVHVVH_SLC_770940_0386_31250906
ds = gdal.Open('../data/RS-2_Wenkai/RS2_20191110_032238_0004_FQ16_HHVVHVVH_SLC_770940_0385_31250903.tif', gdal.GA_ReadOnly)
band = ds.GetRasterBand(1)
arr = band.ReadAsArray()
outname='RS2_20191110_legend.png'
#plt.imshow(arr)
#plt.show()

#refstation for RS-2
#2019-11-10 03:22:00,115.9986393649154,85.82221412196998,295.6981523605136,1.0908295903499685,0.33966405996759874
lon0=115.9986393649154
lat0=85.82221412196998
head0=295.6981523605136





##ALOS-2 scene
##The ALOS-2 image from 10 Nov 10:48:49 UTC.
##The bands are: SHH, SHV, SVH, SVV, Lat, Long, Incident angle. 
#ds = gdal.Open('../data/ALOS-2_Malin/ALOS2-HBQR1_1__A-ORBIT__ALOS2295171790-191110_Cal_ML.tif', gdal.GA_ReadOnly)
#band = ds.GetRasterBand(1)
#arr = band.ReadAsArray()
#outname='ALOS2_20191110.png'

#band=ds.GetRasterBand(5)
#lat = band.ReadAsArray()
#band=ds.GetRasterBand(6)
#lon = band.ReadAsArray()

##scale the values
#arr=10.*np.log10(arr)
#print(np.min(arr))
#print(np.max(arr))
#print(np.mean(arr))
##plt.imshow(arr,vmax=-5,vmin=-25)
##plt.show()

##refstation for ALOS-2
##2019-11-10 10:48:00,116.11873002433686,85.82459083305169,295.83511127916154,1.4818942994101856,0.415055278122272
#lon0=116.11873002433686
#lat0=85.82459083305169
#head0=295.83511127916154


##TSX scene for 2019-11-14
##time stamp is 20191114T042434_20191114T042456
#ds = gdal.Open('../data/TSX_Wenkai/TDX1_SAR__MGD_RE___SC_S_SRA_20191114T042434_20191114T042456.tif', gdal.GA_ReadOnly)
#band = ds.GetRasterBand(1)
#arr = band.ReadAsArray()
#outname='TDX1_20191114.png'
##plt.imshow(arr)
##plt.show()

##ref station for TXS:
##2019-11-14 04:24:00,118.16217076435768,86.15982474551613,300.56654264271526,4.141477302772724,0.6866326529852491
#lon0=118.16217076435768
#lat0=86.15982474551613
#head0=300.56654264271526


if subset==False:
    #second background?
    #RS-2 scene for 31 Dec 2019, 03:35:02 UTC
    tif='../data/RS-2_Wenkai/RS2_20191231_033502_0004_FQ20W_HHVVHVVH_SLC_783865_1107_32077288_HV.tif'
    outname='RS2_20191231_map.png'
    outname='RS2_20191231_map_init.png'
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


    ###The ALOS-2 image from 10 Nov 10:48:49 UTC.
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
    
    ##ALS tif from 21 Jan
    ##time: 20200121T103544-20200121T103614 to 20200121T121616-20200121T121646
    #tif='../data/ALS/20200121_als_merged_grid-stere.tiff'
    #outname='ALS_20200121_map.png'
    #outname='ALS_20200121_map_colors.png'
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
if subset:
    fig1 = plt.figure(figsize=(25,15))
else:
    fig1 = plt.figure(figsize=(35,15))
ax = fig1.add_subplot(111)

if subset==False:
    
    if alos:
        #ALOS-2
        CS1=ax.contourf(rot_x2, rot_y2, arr2, 25,cmap=plt.cm.binary_r, vmax=-5, vmin=-25)
        cb = plt.colorbar(CS1)  # draw colorbar
        cb.set_label(label='Intensity (dB)',fontsize=20)
    else:
        ###for TSX and RS-2
        CS1=ax.contourf(rot_x2, rot_y2, arr2.T, 50,cmap=plt.cm.binary_r)
        cb = plt.colorbar(CS1)  # draw colorbar
        cb.set_label(label='Intensity (dB)',fontsize=20)
        
        ##for ALS
        ##do something about the PS (too high!)
        #arr = np.where(arr2>1.,1.,arr2)
        ##and some low points
        #arr = np.where(arr<0,0,arr)
        #CS2 = plt.contourf(rot_x2, rot_y2, arr.T, 30, vmax=1., vmin=0)#,cmap=plt.cm.binary_r,alpha=1)
        #cb = plt.colorbar(CS2)  # draw colorbar
        #cb.set_label(label='Elevation (m)',fontsize=20)
        
        
        
if subset:
    #for ALS
    #do something about the PS (too high!)
    arr = np.where(arr>1.,1.,arr)
    #and some low points
    arr = np.where(arr<0,0,arr)
    CS2 = plt.contourf(rot_x, rot_y, arr.T, 30, vmax=1., vmin=0,cmap=plt.cm.binary_r,alpha=1)
    cb = plt.colorbar(CS2)  # draw colorbar
    cb.set_label(label='Elevation (m)',fontsize=20)

#limit the region
#ax.set_xlim(-6000,6000)
#ax.set_ylim(-6000,6000)

#ax.set_xlim(-3000,3000)
#ax.set_ylim(-3000,3000)

#ax.set_xlim(-2000,2000)
#ax.set_ylim(-2000,2000)

#transect paper
ax.set_xlim(-7000,2500)
ax.set_ylim(-1400,3700)

if subset:
    ##Sloop
    ax.set_xlim(-750,-165)
    ax.set_ylim(150,650)
    outname='map_Sloop.png'

#larger ticks
ax.tick_params(axis="x", labelsize=18)
ax.tick_params(axis="y", labelsize=18)

#del arr, rot_x, rot_y
gc.collect()

if subset==False:
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
                ax.plot(xx,yy,lw=6,label=loc,c='purple')
            if loc=='Nloop':
                ax.plot(xx,yy,lw=6,label=loc,c='salmon')
                
        ##Nloop start
        #if date=='20191031' and loc=='Nloop':
            #ax.plot(xx,yy,'o',ms=2,c='salmon')
        #snow1, runway
        if date=='20200112':
            if loc=='snow1':
                ax.plot(xx,yy,lw=6,label='snow1',c='gold')
            if loc=='runway':
                ax.plot(xx,yy,lw=6,label='runway',c='deeppink')
        #long
        if date=='20200123':
            ax.plot(xx,yy,lw=6,label='long',c='c')
        #event
        if date=='20200126' and loc=='special':
            ax.plot(xx,yy,lw=6,label='event',c='darkred')
        #dark side FYI
        if date=='20200107' and loc=='special':
            ax.plot(xx,yy,lw=6,label='dark FYI',c='darkkhaki')
        #dark side SYI
        if date=='20200115' and loc=='special':
            ax.plot(xx,yy,lw=6,label='dark SYI',c='b')
        ##dranitsyn lead
        #if date=='20200226':
            #ax.plot(xx,yy,lw=6,label='dranitsyn',c='y')
        ##RS site, leg 3
        #if date=='20200430':
            #if loc=='special':
                #ax.plot(xx,yy,lw=6,label='RS site',c='darkkhaki')
            
        #Allies Ridge
        if date=='20200228':
            if loc=='ridgeA1':
                ax.plot(xx,yy,lw=6,label='ridge',c='limegreen')
            else:
                ax.plot(xx,yy,lw=6,c='limegreen')
        #Fort Ridge
        if date=='20200221':
            ax.plot(xx,yy,lw=6,c='limegreen')
        if date=='20200131' and loc=='ridgeFR3':
            ax.plot(xx,yy,lw=6,c='limegreen')
        #Davids Ridge
        if date=='20200424' and loc=='ridgeD':
            ax.plot(xx,yy,lw=6,c='limegreen')
        if date=='20200424' and loc=='ridgeE':
            ax.plot(xx,yy,lw=6,c='limegreen')
            
        del xx,yy
            
    #and from CO2
    from scipy import ndimage
    inpath_grid = '../data/grids_AGU/'
    locs=['transect','albedoLD','albedoRBB']
    cols=['orange','indigo','cornflowerblue']
    date='20200630'
    stp='1'
    method_gem2='nearest'
    ch_name='_18kHz'

    i=0
    for loc in locs:
        of = inpath_grid+loc+'_'+date+'_'+stp+'m_'+method_gem2+ch_name+'.npz'
        print(of)

        data = np.load(of)
        x_grid = data['x']
        y_grid = data['y']
        i_grid = data['ice']

        del data

        #shift relativelly to match CO1 local coordinates
        x_grid = ndimage.rotate(x_grid, 40, reshape=False,order=0,mode='nearest')
        y_grid = ndimage.rotate(y_grid, 40, reshape=False,order=0,mode='nearest')

        x_grid = x_grid+1320
        y_grid = y_grid+10

        ##assign a unique value to the track
        i_grid = np.where(i_grid>0,1,0)

        ##plot
        xx=np.ma.array(x_grid,mask=i_grid==0).compressed().flatten()
        yy=np.ma.array(y_grid,mask=i_grid==0).compressed().flatten()
        
        if loc=='transect':
            plt.plot(xx,yy,'o',ms=5,label=loc,c=cols[i]); i=i+1
        else:
            plt.plot(xx,yy,lw=6,label=loc,c=cols[i]); i=i+1
        
        del xx,yy,x_grid,y_grid,i_grid

    ##initial survey of leg 4
    #inpath_grid = '../data/grids_AGU/'
    #locs=['special']
    #cols=['y']
    #date='20200617'
    #stp='1'
    #method_gem2='nearest'
    #ch_name='_18kHz'

    #i=0
    #for loc in locs:
        #of = inpath_grid+loc+'_'+date+'_'+stp+'m_'+method_gem2+ch_name+'.npz'
        #print(of)

        #data = np.load(of)
        #x_grid = data['x']
        #y_grid = data['y']
        #i_grid = data['ice']

        #del data

        ##shift relativelly to match CO1 local coordinates
        #x_grid = ndimage.rotate(x_grid, 40, reshape=False,order=0,mode='nearest')
        #y_grid = ndimage.rotate(y_grid, 40, reshape=False,order=0,mode='nearest')
        
        #x_grid = x_grid+1200
        #y_grid = y_grid+150

        ###assign a unique value to the track
        #i_grid = np.where(i_grid>0,1,0)

        ###plot
        #xx=np.ma.array(x_grid,mask=i_grid==0).compressed().flatten()
        #yy=np.ma.array(y_grid,mask=i_grid==0).compressed().flatten()
        #plt.plot(xx,yy,lw=6,label=loc,c=cols[i]); i=i+1
        
        #del xx,yy,x_grid,y_grid,i_grid
        
    plt.legend(fontsize=25,fancybox=True,framealpha=.9,ncol=3,loc='upper right')

if subset:
    fname='../data/classes_Sloop20200116.csv'
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
    
    cmap = ListedColormap(["purple", "b", "c"])
    ax.scatter(xx,yy,c=cls,cmap=cmap)
    #ax.scatter(xx,yy,c=si)
    #ax.scatter(xx,yy,c=it)
    
    




fig1.savefig(outpath+outname,bbox_inches='tight')
