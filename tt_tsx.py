import numpy as np
from osgeo import gdal, osr
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from datetime import datetime, timedelta
from glob import glob
from tt_func import getColumn, proj_sat
import gc
from scipy.signal import savgol_filter


#reference heading in Floenavi: 301.63560882616076

#20191115T040723_20191115T040745
#20191215T032423_20191215T032445
#20200112T034138_20200116T034200
#20200213T055044_20200216T055106
#20200317T095226_20200317T095248
#20200328T112657_20200328T112719

inpath='../data/TSX_Wenkai/classified_geotiffs/'
inpath='../data/TSX_Wenkai/classified_geotiffs_new/'
inpath_cls='../data/classes_tsx/'
outpath='../plots_tsx/3x3km_revision/'

dates=['20191115','20191215','20200108','20200112','20200213','20200317','20200328']
dates=['20191115','20191215','20200112','20200213','20200317','20200328']   #for paper

#dates=['20191115']  #test


intensity_window=16; window_name='4x4';npixels=4
polyorder = 3

goodness1=[]
goodness2=[]
#start goodness plot
fig2 = plt.figure(figsize=(10,5))
cx = fig2.add_subplot(111)

#Wenkai's 'favorite' sea ice classification scheme
#class 3: 0,100,255         leads                   
#class 5: 12,147,12         DYI                 
#class 6: 130, 204, 133     BYI                    parts of long 
#class 7: 255,255,0         LFY                    runway, Sloop, parts of long
#class 9: 200,0,0           DMYI                   parts of Sloop, Event
#class 10: 200,111,111      BMYI/DefFYI            Nloop, parts of dark site transects

#From paper
#4. Level FYI (LFYI): smooth FYI areas having intermediate HH intensities, between leads and DYI ($-25$ dB and $-15$ dB).
#5. Dark MYI (DMYI): MYI with relatively low HH intensities (between $-15$ dB and $-10$ dB). The majority of MYI areas are in this class, which is assumed to be MYI with less deformation. In this study, second-year ice (SYI) is grouped into the MYI category.
#6. Bright MYI or deformed FYI (BMYI/DefFYI): thick ice (FYI or MYI) surfaces having relatively high HH intensities ($\geq-10$ dB).

#Make averages over these 3 classes and fit the line. Do log-log plot.


class_cm = ListedColormap([
    [0/255,100/255,255/255,255/255],
    [0,0,0,0],
    [12/255,147/255,12/255,255/255],
    [130/255, 204/255,133/255,255/255],
    [255/255,255/255,0/255,255/255],
    [0,0,0,0],
    [200/255,0/255,0/255,255/255],
    [200/255,111/255,111/255,255/255]])

for dt in dates:
    print(dt)
    fn1 = glob(inpath+dt+'*_HH.tif')[0]
    fn2 = glob(inpath+dt+'*_classified.tif')[0]
    outname='TSX_'+dt+'.png'
    #ds = gdal.Open(fn2, gdal.GA_ReadOnly)
    #band = ds.GetRasterBand(1)
    #arr = band.ReadAsArray()
    #plt.imshow(arr)
    #plt.show()
    #print(np.min(arr))
    #print(np.max(arr))
    #exit()
    
    #some colormap problems - dirty fix
    if dt=='20191115' or dt=='20200328':
        class_cm = ListedColormap([
            [0/255,100/255,255/255,255/255],
            [0,0,0,0],
            [12/255,147/255,12/255,255/255],
            [130/255, 204/255,133/255,255/255],
            [255/255,255/255,0/255,255/255],
            [0,0,0,0],
            [200/255,0/255,0/255,255/255],
            [200/255,111/255,111/255,255/255]])
    else:
        class_cm = ListedColormap([
            [0,0,0,0],
            [0,0,0,0],
            [0/255,100/255,255/255,255/255],
            [0,0,0,0],
            [12/255,147/255,12/255,255/255],
            [130/255, 204/255,133/255,255/255],
            [255/255,255/255,0/255,255/255],
            [0,0,0,0],
            [200/255,0/255,0/255,255/255],
            [200/255,111/255,111/255,255/255]])
    
    
     
    #ref station for TXS:    
    if dt=='20191115':
        #20191115T040723_20191115T040745
        #2019-11-15 04:07:00,118.33855681784216,86.18978408879255,299.1155733031989,2.0283310777603796,0.5176443862778968
        lon0=118.33855681784216
        lat0=86.18978408879255
        head0=299.1155733031989
        
        rug_fn = [inpath_cls+'classes_Sloop20191114.csv',inpath_cls+'classes_Nloop20191114.csv']
    
    if dt=='20191215':
        #20191215T032423_20191215T032445
        #2019-12-15 03:24:00,118.13309624173567,86.61880125326061,293.69796087206294,1.809896045793524,0.41744617630710235
        lon0=118.13309624173567
        lat0=86.61880125326061
        head0=293.69796087206294
        
        rug_fn = [inpath_cls+'classes_Sloop20191205.csv',inpath_cls+'classes_Nloop20191205.csv']
        
    if dt=='20200108':
        #20200108T042427_20200108T042449
        #2020-01-08 04:24:00,115.20440219181685,87.11089584512887,301.2193853959709,4.644832135872137,1.1834063644069477
        lon0=115.20440219181685
        lat0=87.11089584512887
        head0=301.2193853959709
        
        rug_fn = [inpath_cls+'classes_Sloop20200116.csv',inpath_cls+'classes_Nloop20200116.csv',inpath_cls+'classes_runway20200112.csv',inpath_cls+'classes_snow120200112.csv',inpath_cls+'classes_recon20200107.csv',inpath_cls+'classes_special20200107.csv',inpath_cls+'classes_special20200115.csv',inpath_cls+'classes_ridgeFR120200119.csv',inpath_cls+'classes_ridgeA120200117.csv']
    
    if dt=='20200112':
        #20200112T034138_20200116T034200
        
        #2020-01-12 03:41:00,109.99937125251066,87.26208996286708,298.75119555621717,5.8614527134766465,2.1244788899482194
        lon0=109.99937125251066
        lat0=87.26208996286708
        head0=298.75119555621717
        
        rug_fn = [inpath_cls+'classes_Sloop20200116.csv',inpath_cls+'classes_Nloop20200116.csv',inpath_cls+'classes_runway20200112.csv',inpath_cls+'classes_snow120200112.csv',inpath_cls+'classes_recon20200107.csv',inpath_cls+'classes_special20200107.csv',inpath_cls+'classes_special20200115.csv',inpath_cls+'classes_special20200123.csv',inpath_cls+'classes_recon20200126.csv',inpath_cls+'classes_special20200126.csv',inpath_cls+'classes_ridgeFR120200119.csv',inpath_cls+'classes_ridgeA120200117.csv']

    if dt=='20200213':
        #20200213T055044_20200216T055106
        #2020-02-13 05:50:00,85.15144901470352,87.94738928916001,276.682326681203,4.456229160783077,0.9302815730387157
        lon0=85.15144901470352
        lat0=87.94738928916001
        head0=276.682326681203
        
        rug_fn = [inpath_cls+'classes_Sloop20200220.csv',inpath_cls+'classes_Nloop20200220.csv',inpath_cls+'classes_runway20200207.csv',inpath_cls+'classes_snow120200207.csv',inpath_cls+'classes_ridgeFR120200221.csv',inpath_cls+'classes_ridgeFR220200221.csv',inpath_cls+'classes_ridgeA120200228.csv',inpath_cls+'classes_recon20200228.csv',inpath_cls+'classes_recon20200226.csv']

    if dt=='20200317':
        #20200317T095226_20200317T095248
        #2020-03-17 09:52:00,12.362527398569497,86.78831010296078,200.224132058465,3.7297813713179213,0.89337834329511
        lon0=12.362527398569497
        lat0=86.78831010296078
        head0=200.224132058465
        
        rug_fn = [inpath_cls+'classes_Sloop20200330.csv',inpath_cls+'classes_Nloop20200326.csv']
        
    if dt=='20200328':
        #20200328T112657_20200328T112719
        #2020-03-28 11:27:00,13.270078611108508,85.5951255232772,196.48183819244613,8.66019779558356,2.614077980232676
        lon0=13.270078611108508
        lat0=85.5951255232772
        head0=196.48183819244613
        
        rug_fn = [inpath_cls+'classes_Sloop20200330.csv',inpath_cls+'classes_Nloop20200326.csv']
    
    arr1,rot_x1,rot_y1=proj_sat(fn1,lon0,lat0,head0,alos=False,spacing=1,band=1,ps_pos=True)

    #arr2 has same coordinates, just read the data
    ds = gdal.Open(fn2, gdal.GA_ReadOnly)
    band = ds.GetRasterBand(1)
    arr2 = band.ReadAsArray()
    
    ##some reclassification for some dates
    #if dt=='20191115':
        #arr2 = np.where(arr2>10,10,arr2)

    #manual position corrections    
    if dt=='20191115':
        rot_x1 = rot_x1+40
        rot_y1 = rot_y1+40
        
    if dt=='20191215':
        rot_x1 = rot_x1+60
        rot_y1 = rot_y1+40
        
    if dt=='20200108':
        rot_x1 = rot_x1+50
        rot_y1 = rot_y1+50
        
    if dt=='20200112':
        rot_x1 = rot_x1+240
        rot_y1 = rot_y1+85
        
    if dt=='20200213':
        rot_x1 = rot_x1-540
        rot_y1 = rot_y1+320
    
    if dt=='20200317':
        rot_x1 = rot_x1+0
        rot_y1 = rot_y1-50
    
    if dt=='20200328':
        rot_x1 = rot_x1+10
        rot_y1 = rot_y1-40
    
    #Wenkai masks no values as 999
    arr1 = np.ma.array(arr1,mask=arr1==999)
    
    #setup figure
    fig1 = plt.figure(figsize=(22,10))
    
    ax = fig1.add_subplot(121)
    #dont have any ticks
    ax.set_xticks([])
    ax.set_xticks([], minor=True)
    ax.set_yticks([])
    ax.set_yticks([], minor=True)
    
    
    CS1=ax.contourf(rot_x1, rot_y1, arr1.T, 50,cmap=plt.cm.binary_r)
    
    bx = fig1.add_subplot(122)
    #dont have any ticks
    bx.set_xticks([])
    bx.set_xticks([], minor=True)
    bx.set_yticks([])
    bx.set_yticks([], minor=True)
    
    CS2=bx.contourf(rot_x1, rot_y1, arr2.T, 10,cmap=class_cm)
    #cb = plt.colorbar(CS1)  # draw colorbar
    #cb.set_label(label='Intensity (dB)',fontsize=20)

    #limit the region
    ax.set_xlim(-2000,2000)
    ax.set_ylim(-2000,2000)
    
    bx.set_xlim(-2000,2000)
    bx.set_ylim(-2000,2000)
    
    
    
    ##larger ticks
    #ax.tick_params(axis="x", labelsize=18)
    #ax.tick_params(axis="y", labelsize=18)
    
    #bx.tick_params(axis="x", labelsize=18)
    #bx.tick_params(axis="y", labelsize=18)

    #plot/compare with some transect data
    
    #mask arrays
    data=arr2.T; mask = arr1.T.mask
    del arr1,arr2; gc.collect()
    data=np.ma.array(data,mask=mask).compressed()
    rot_x1=np.ma.array(rot_x1,mask=mask).compressed()
    rot_y1=np.ma.array(rot_y1,mask=mask).compressed()
    

    good_data1 = 0   #collect goodness count
    good_data2 = 0   #collect goodness count
    all_data = 0
    for fname in rug_fn:
        print(fname)

        xx = getColumn(fname,0, delimiter=',')
        xx = np.array(xx,dtype=np.float)

        yy = getColumn(fname,1, delimiter=',')
        yy = np.array(yy,dtype=np.float)
        
        std = getColumn(fname,5, delimiter=',')
        std = np.array(std,dtype=np.float)
        
        #some positioning adjustment for Sloop in March
        loc=fname.split('_')[-1].split('20')[0]
        if (loc=='Sloop') & (dt=='20200317'):
            xx = xx-210
            yy = yy+280
        
        if (loc=='Sloop') & (dt=='20200328'):
            xx = xx-130
            yy = yy+100

        #get smooting window size/sampling interval - here we use 4 pixel size: ~positioning error + ~roughness feature size
        #how many measurements in one/three TSX pixel size, this depends on MP sampling spacing (1-3m)
        #get mean distance between fixed date MP points
        dx = xx[1:]-xx[:-1]
        dy = yy[1:]-yy[:-1]
        md = np.mean(np.sqrt(dx**2+dy**2))
        
        window = int(npixels*8/md); #print(window)
        #window has to be an odd number
        if np.mod(window,2)==0: window=window+1; #print(window)
        try:
            std = savgol_filter(std, window, polyorder)
        except:
            continue    #sometimes there is not enough data to apply the smoothing filter
        
        #take a value for every pixel/every 3 pixels and every roughness feature scale (24 m is again a good first guess)
        #this depends on the measurement spacing
        #WARNING: in order this to work the spacing needs to be homogeneous - currently recond data needs to be manually edited - MP part of the transects needs to removed
        xx = xx[::window]
        yy = yy[::window]
        std = std[::window]        
        
        #color-code entire transects by roughness (or ice age)
        rubble = .2
        ridge = .3
        
        #code by locs:
        cls=np.ones_like(std)
        loc=fname.split('_')[-1].split('20')[0]
        loc_dt = fname.split('_')[-1].split(loc)[-1].split('.')[0]
        print(loc,loc_dt)
        if loc=='Nloop':
            cls=np.where(std<rubble,cls*9,cls*10)
        elif loc=='runway':
            cls=np.where(std<rubble,cls*7,cls*9)
        elif loc=='Sloop':
            cls=np.where(std<rubble,cls*7,cls*9)
        elif (loc=='special') & (loc_dt=='20200107'):
            cls=np.where(std<rubble,cls*7,cls*10)
        elif (loc=='special') & (loc_dt=='20200115'):
            cls=np.where(std<rubble,cls*9,cls*10)    
        elif (loc=='special') & (loc_dt=='20200123'):   #long transect
            cls=np.where(std<rubble,cls*7,cls*9)
            #cls=np.where(std<rubble,cls*6,cls)
        elif (loc=='special') & (loc_dt=='20200126'):
            cls=np.where(std<rubble,cls*7,cls*9)
        elif loc=='recon':                              #this was a ski-do transect, larger footprint, different threshold necessary?
            cls=np.where(std<rubble,cls*7,cls*9)
        elif (loc=='recon') & (loc_dt=='20200107'):                              #this was a ski-do transect, larger footprint, different threshold necessary?
            cls=np.where(std<rubble,cls*9,cls*10)
            
        elif (loc=='ridgeFR1') | (loc=='ridgeA1')| (loc=='ridgeFR2'):
            cls=np.where(std<rubble,cls*9,cls*10)
        else:
            cls=cls*7

        #code uniformly
        #use 2 thresholds: smooth - rough -rougher (level - deformed - very deformed)
        #deformed: influenced by 1 deformation fature (linear/one directional feature, one deformation event)
        #very deforemd: influenced by multiple deformation features (multiple directional feature, several deformation events)
        
        
        
        
        #ax.scatter(xx,yy,c=std,s=4,cmap=plt.cm.Blues,vmin=0,vmax=.5)
        ax.scatter(xx,yy,c=cls,cmap=class_cm,s=25,vmin=1,vmax=11)#,ec='k')
        
        #pin zero,zero to see how it compares to PS in HH
        #ax.scatter(0,0,marker='*',s=3,c='g')
                
        #ice roughness - sigma - std
        bx.scatter(xx,yy,c=std,s=25,cmap=plt.cm.Blues,vmin=0,vmax=.5)#,ec='k')
            
        #Can we track the algorithm score/goodness test?
        #Count in how many cases out of all, the algorithm gets the ice in the same class as the roughness from transects...
        
        #only repeated/gridded transects
        if loc in ['Nloop','Sloop','runway','snow1']:#,'recon','special']:
            hh_mean=[]
            for i in range(0,len(xx)):
                dx = xx[i]-rot_x1
                dy = yy[i]-rot_y1
                d = np.sqrt(dx**2+dy**2)
                
                tran = cls[i]
                all_data=all_data+1
                
                #clossest in classified image
                sar = data[np.argmin(np.abs(d))]
                if sar==tran: good_data1=good_data1+1
                
                #take a 4x4 window and check if any value inside matches
                sar = data[np.argsort(np.abs(d))[:intensity_window]]
                if tran in sar: good_data2=good_data2+1
                
    #get goodness ratio
    print('goodness ratio:')
    print(good_data1/all_data)
    print(good_data2/all_data)
    
    goodness1.append(good_data1/all_data*100)
    goodness2.append(good_data2/all_data*100)

    #plt.show()
    fig1.savefig(outpath+outname,bbox_inches='tight')
    plt.close(fig1)
    
    del data, mask, rot_x1, rot_y1
    gc.collect()

x1 = [ datetime.strptime(x, "%Y%m%d") for x in dates ]
#td1 = timedelta(days=2)
#x2 = [ y+td1 for y in x1]

#import ipdb; ipdb.set_trace()

#cx.bar(x2,goodness1,width=2,label='closest')
cx.bar(x1,goodness2,width=5,label='4x4 window')

#cx.legend(loc='lower left',fontsize=20)

#cx.set_xlabel('Roughness') # X axis data label
cx.set_ylabel('Goodness (%)') # Y axis data label

#cx.set_xlim(-.1,3.1)
#cx.set_ylim(-23,0)

#dates_m = ['20191101','20191201','20200101','20200201','20200301','20200401']
#dt_m = [ datetime.strptime(x, '%Y%m%d') for x in dates_m ]
#dt_diff = [ (x-x1[0]).days for x in dt_m ]

#import ipdb; ipdb.set_trace()

#plt.xticks(dt_diff, ['1 Nov','1 Dec','1 Jan','1 Feb','1 Mar','1 Apr'])
#cx.set_xticks(dt_diff)

##cx.set_xticklabels(['2019-11','2019-12','2020-01','2020-02','2020-03','2020-4'])

#cx.set_xlim(datetime(2019,11,1),datetime(2020,4,1))

fig2.autofmt_xdate()

fig2.savefig(outpath+'goodness',bbox_inches='tight')
plt.close(fig2)

#some thoughts about the meaning of this:
#SAR and in particular x-band is sensitive to small roughness (SSL, bubbles, brine pockets, frost flowers) and larger-scale rougness (deformed ice)
#the first one is well detectable in the Fortress and in some bright YI
#the second one is particulary interesting as this larger-scale roughness can be of various scales from half-a-meter (cracks, rubble blocks) to several 10-m (large rubble, ridges)
#it seems like the X-band detects best roughness starting somewhere at a pixel size ~5 meters
#an observer on the ice will see also much smaller roughness (rubble)
#for this reason we used a single combined roughness treshold and not two separate as in Itkin et al (transect paper): we distingush just between level ice and deformed ice

#terms: volumetric and geometric roughness/scattering

#presentation of Randy: scatter plots of roughness and HH annd HV intensity. realtionship with HV is more linear. HH looks more exponential. Low intensities can have quite some roughness

#discusson with Randy
#the roughness treshold to be significant/detectable by SAR should depend also on the IA: low angles should see smaller/lower objects.

#Wenkai and Randy should get in contact and talk a bit about synergies of X- and L-band processing for roughness on MOSAiC case

#another obvious point: BYI and rough MYI (frozen SSL) look the same as they both have a lot of volumetric scattering/roughness

#for Randy
#The only way to pin the elevation/roughness at wich the geometric scattering becomes significant is use landfast ice data. At MOSAiC the co-lation of TSX and ALS turned out to be impossible. In Karl's paper there is only qualitative analysis.
#if we take there treshold from CAA and use it MOSAiC this will be a great way forward!

#Fow Wenkai:
#extract intensities from TSX images and correlate to sea ice thickness and surface roughness over transect data
#make different curves for different dates - label with IA

#Limitations: any mismatch in brightness-roughnes could be consequnce of the nature of the roughness - derived from thickness (sail-less ridges?)

#long transects: two leads were deforemd in fresh ridges during that transect and not visible on the classified map. But they are very narrow and not appear on the February HH brigtness. Likely a footprint issue. The ridges are about 10-20 m accross. Likely the keel is more massive and more visible in the roughness data derived by GEM-2
