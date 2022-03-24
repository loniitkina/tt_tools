import numpy as np
from osgeo import gdal, osr
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from datetime import datetime
from glob import glob
from tt_func import getColumn, proj_sat
import gc


#reference heading in Floenavi: 301.63560882616076

#20191115T040723_20191115T040745
#20191215T032423_20191215T032445
#20200112T034138_20200116T034200
#20200213T055044_20200216T055106
#20200317T095226_20200317T095248
#20200328T112657_20200328T112719

inpath='../data/TSX_Wenkai/classified_geotiffs/'
inpath_cls='../data/'
outpath='../plots_tsx/'

dates=['20191115','20191215','20200108','20200112','20200213','20200317','20200328']
#dates=['20200317','20200328']

#Wenkai's favorite sea ice classification scheme
#class 3: 0,100,255         leads                   
#class 5: 12,147,12         DYI                 
#class 6: 130, 204, 133     BYI                    parts of long 
#class 7: 255,255,0         LFY                    runway, Sloop, parts of long
#class 9: 200,0,0           DMYI                   parts of Sloop, Event
#class 10: 200,111,111      BMYI/DefFYI            Nloop, parts of dark site transects

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


for dt in dates:
    print(dt)
    fn1 = glob(inpath+dt+'*_HH.tif')[0]
    fn2 = glob(inpath+dt+'*_classified.tif')[0]
    outname=outpath+'TSX_'+dt+'.png'
    #ds = gdal.Open(fn2, gdal.GA_ReadOnly)
    #band = ds.GetRasterBand(1)
    #arr = band.ReadAsArray()
    #plt.imshow(arr)
    #plt.show()
    ##exit()

    #ref station for TXS:
    if dt=='20191115':
        #20191115T040723_20191115T040745
        #2019-11-15 04:07:00,118.33855681784216,86.18978408879255,299.1155733031989,2.0283310777603796,0.5176443862778968
        lon0=118.33855681784216
        lat0=86.18978408879255
        head0=299.1155733031989
        
        #closest in time classes/ice thickness files
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
        
        rug_fn = [inpath_cls+'classes_Sloop20200116.csv',inpath_cls+'classes_Nloop20200116.csv',inpath_cls+'classes_runway20200112.csv',inpath_cls+'classes_snow120200112.csv',inpath_cls+'classes_special20200107.csv',inpath_cls+'classes_special20200115.csv',inpath_cls+'classes_ridgeFR120200119.csv',inpath_cls+'classes_ridgeA120200117.csv']
    
    if dt=='20200112':
        #20200112T034138_20200116T034200
        #2020-01-12 03:42:00,109.99808909889244,87.26211346213222,298.73636895777037,5.871213449869556,2.131144912486477
        
        lon0=109.99808909889244
        lat0=87.26211346213222
        head0=298.73636895777037
        
        #2020-01-12 03:41:00,109.99937125251066,87.26208996286708,298.75119555621717,5.8614527134766465,2.1244788899482194
        lon0=109.99937125251066
        lat0=87.26208996286708
        head0=298.75119555621717
        
        
        rug_fn = [inpath_cls+'classes_Sloop20200116.csv',inpath_cls+'classes_Nloop20200116.csv',inpath_cls+'classes_runway20200112.csv',inpath_cls+'classes_snow120200112.csv',inpath_cls+'classes_special20200107.csv',inpath_cls+'classes_special20200115.csv',inpath_cls+'classes_special20200123.csv',inpath_cls+'classes_special20200126.csv',inpath_cls+'classes_ridgeFR120200119.csv',inpath_cls+'classes_ridgeA120200117.csv']

    if dt=='20200213':
        #20200213T055044_20200216T055106
        #2020-02-13 05:50:00,85.15144901470352,87.94738928916001,276.682326681203,4.456229160783077,0.9302815730387157
        lon0=85.15144901470352
        lat0=87.94738928916001
        head0=276.682326681203
        
        rug_fn = [inpath_cls+'classes_special20200123.csv',inpath_cls+'classes_special20200126.csv',inpath_cls+'classes_Sloop20200220.csv',inpath_cls+'classes_Nloop20200220.csv',inpath_cls+'classes_runway20200207.csv',inpath_cls+'classes_ridgeFR120200221.csv',inpath_cls+'classes_ridgeFR220200221.csv',inpath_cls+'classes_ridgeA120200228.csv',inpath_cls+'classes_recon20200228.csv']

    if dt=='20200317':
        #20200317T095226_20200317T095248
        #2020-03-17 09:52:00,12.362527398569497,86.78831010296078,200.224132058465,3.7297813713179213,0.89337834329511
        lon0=12.362527398569497
        lat0=86.78831010296078
        head0=200.224132058465
        
        rug_fn = [inpath_cls+'classes_Sloop20200305.csv',inpath_cls+'classes_Nloop20200305.csv']
        
    if dt=='20200328':
        #20200328T112657_20200328T112719
        #2020-03-28 11:27:00,13.270078611108508,85.5951255232772,196.48183819244613,8.66019779558356,2.614077980232676
        lon0=13.270078611108508
        lat0=85.5951255232772
        head0=196.48183819244613
        
        rug_fn = [inpath_cls+'classes_Sloop20200330.csv',inpath_cls+'classes_Nloop20200326.csv']
    
    arr1,rot_x1,rot_y1=proj_sat(fn1,lon0,lat0,head0,alos=False,spacing=1,band=1,ps_pos=True)
    arr2,rot_x2,rot_y2=proj_sat(fn2,lon0,lat0,head0,alos=False,spacing=1,band=1,ps_pos=True)
    
    #manual position corrections
    #for some dates PS is not at the origin on the satellite scenes - fix that
    if dt=='20200112':
        rot_x1 = rot_x1+200
        rot_y1 = rot_y1+50
        
        rot_x2 = rot_x2+200
        rot_y2 = rot_y2+50

    if dt=='20200213':
        rot_x1 = rot_x1-600
        rot_y1 = rot_y1+250
        
        rot_x2 = rot_x2-600
        rot_y2 = rot_y2+250
    
    #Wenkai masks no values as 999
    arr1 = np.where(arr1==999,0,arr1)

    #setup figure
    fig1 = plt.figure(figsize=(22,10))
    
    ax = fig1.add_subplot(121)
    CS1=ax.contourf(rot_x1, rot_y1, arr1.T, 50,cmap=plt.cm.binary_r)
    
    bx = fig1.add_subplot(122)
    CS2=bx.contourf(rot_x2, rot_y2, arr2.T, 10,cmap=class_cm)
    #cb = plt.colorbar(CS1)  # draw colorbar
    #cb.set_label(label='Intensity (dB)',fontsize=20)

    #limit the region
    ax.set_xlim(-7000,3000)
    ax.set_ylim(-5000,5000)
    
    bx.set_xlim(-7000,3000)
    bx.set_ylim(-5000,5000)

    #larger ticks
    ax.tick_params(axis="x", labelsize=18)
    ax.tick_params(axis="y", labelsize=18)
    
    bx.tick_params(axis="x", labelsize=18)
    bx.tick_params(axis="y", labelsize=18)

    del arr1, arr2, rot_x1, rot_y1, rot_x2, rot_y2
    gc.collect()

    #plot some transect data
    for fname in rug_fn:
        print(fname)

        xx = getColumn(fname,0, delimiter=',')
        xx = np.array(xx,dtype=np.float)

        yy = getColumn(fname,1, delimiter=',')
        yy = np.array(yy,dtype=np.float)

        rug = getColumn(fname,2, delimiter=',')
        rug = np.array(rug,dtype=np.float)

        si = getColumn(fname,3, delimiter=',')
        si = np.array(si,dtype=np.float)

        it = getColumn(fname,4, delimiter=',')
        it = np.array(it,dtype=np.float)

        ##ice thickness
        #ax.scatter(xx,yy,c=it,s=5,cmap=plt.cm.Reds,vmin=0,vmax=5)
        
        ##roughness classes
        #cmap = ListedColormap(["purple", "b", "c"])
        #ax.scatter(xx,yy,c=rug,cmap=cmap,s=5)
        
        #try with rubble thereshold 0.2 for TSX!
        
        
        
        
        
        
        
        
        #color-code entire transects as ice age
        #code by locs:
        cls=np.ones_like(rug)
        loc=fname.split('_')[-1].split('20')[0]
        loc_dt = fname.split('_')[-1].split(loc)[-1].split('.')[0]
        print(loc,loc_dt)
        if loc=='Nloop':
            cls=cls*10
        elif loc=='runway':
            cls=np.where(rug<3,cls*7,cls*9)
        elif loc=='Sloop':
            cls=np.where(rug<3,cls*7,cls*9)
        elif (loc=='special') & (loc_dt=='20200107'):
            cls=np.where(rug<3,cls*7,cls*10)
        elif (loc=='special') & (loc_dt=='20200115'):
            cls=cls*10    
        elif (loc=='special') & (loc_dt=='20200123'):   #long transect
            cls=np.where(rug<3,cls*7,cls*9)
            #cls=np.where(rug<3,cls*6,cls)
        elif (loc=='special') & (loc_dt=='20200126'):
            cls=np.where(rug<3,cls*7,cls*9)
        elif loc=='recon':                              #this was a ski-do transect, larger footprint, different threshold necessary?
            cls=np.where(rug<3,cls*7,cls*9)
            
        elif (loc=='ridgeFR1') | (loc=='ridgeA1')| (loc=='ridgeFR2'):
            cls=cls*10
        else:
            cls=cls*7
        
        #some positioning adjustment for Sloop in March
        if (loc=='Sloop') & (dt=='20200317'):
            xx = xx-210
        
        if (loc=='Sloop') & (dt=='20200328'):
            yy = yy+230
            
        #long transect needs that too!!!

        
        ax.scatter(xx,yy,c=cls,cmap=class_cm,s=4,vmin=1,vmax=11)    
        
        
        #ice thickness
        bx.scatter(xx,yy,c=it,s=4,cmap=plt.cm.Blues,vmin=0,vmax=5)
        
    fig1.savefig(outpath+outname,bbox_inches='tight')
    plt.close(fig1)
    #exit()


#some thoughts about the meaning of this:
#SAR and in particular x-band is sensitive to small roughness (SSL, bubbles, brine pockets, frost flowers) and larger-scale rougness (deformed ice)
#the first one is well detectable in the Fortress and in some bright YI
#the second one is particulary interesting as this larger-scale roughness can be of various scales from half-a-meter (cracks, rubble blocks) to several 10-m (large rubble, ridges)
#it seems like the X-band detects best roughness starting somewhere at a pixel size ~5 meters
#an observer on the ice will see also much smaller roughness (rubble)
#for this reason we used a single combined roughness treshold and not two separate as in Itkin et al (transect paper): we distingush just between level ice and deformed ice
