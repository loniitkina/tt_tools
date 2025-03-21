import numpy as np
from osgeo import gdal, osr
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from datetime import datetime
from glob import glob
from tt_func import getColumn, proj_sat, logfit
import gc
from scipy.signal import savgol_filter

#for debugging
#import ipdb; ipdb.set_trace()

#reference heading in Floenavi: 301.63560882616076

#replot with multifrequnecy data to show consolidation ratio


inpath='../data/TSX_Wenkai/classified_geotiffs_new/'
inpath_table = '../data/ridges_multif/'
outpath='../plots_ridges/'


dates=['20191215','20200112','20200213','20200317','20200328']
dates=['20191215']

scatter=False
intensity_window=81; window_name='9x9';npixels=9 #used in paper
#intensity_window=49; window_name='7x7';npixels=6 
#intensity_window=16; window_name='4x4';npixels=4 #4x4
#intensity_window=9; window_name='3x3';npixels=3 #3x3
#intensity_window=4; window_name='2x2';npixels=2 #2x2 
intensity_window=1; window_name='1x1';npixels=1 #no averaging  - for power curve in the paper
polyorder = 3
if npixels<3:
    polyorder = 2
else:
    polyorder = 3

#dates=['20191005','20191016','20191031']
#scatter=False

fig3 = plt.figure(figsize=(10,10))
ccx = fig3.add_subplot(111)
x_data=[]
y_data=[]

for dt in dates:
    print(dt)
    fn1 = glob(inpath+dt+'*_HH.tif')[0]
    #fn1 = glob(inpath+dt+'*_HH_IAcorrected.tif')[0]
    outname='TSX_icechart'+dt+'.png'
    #ds = gdal.Open(fn2, gdal.GA_ReadOnly)
    #band = ds.GetRasterBand(1)
    #arr = band.ReadAsArray()
    #plt.imshow(arr)
    #plt.show()
    ##exit()

    #ref station for TXS:
    #and closest in time classes/ice thickness files
    
    
    if dt=='20191215':
        #20191215T032423_20191215T032445
        #2019-12-15 03:24:00,118.13309624173567,86.61880125326061,293.69796087206294,1.809896045793524,0.41744617630710235
        lon0=118.13309624173567
        lat0=86.61880125326061
        head0=293.69796087206294
        
        rug_fn = [inpath_table+'mosaic_gem-2+mp_20191205_Sloop_2.csv',inpath_table+'mosaic_gem-2+mp_20191205_Nloop_2.csv']
        
    if dt=='20200108':
        #20200108T042427_20200108T042449
        #2020-01-08 04:24:00,115.20440219181685,87.11089584512887,301.2193853959709,4.644832135872137,1.1834063644069477
        lon0=115.20440219181685
        lat0=87.11089584512887
        head0=301.2193853959709
        
        rug_fn = [inpath_table+'classes_Sloop20200116.csv',inpath_table+'classes_Nloop20200116.csv',inpath_table+'classes_runway20200112.csv',inpath_table+'classes_snow120200112.csv',inpath_table+'classes_recon20200107.csv',inpath_table+'classes_special20200107.csv',inpath_table+'classes_special20200115.csv',inpath_table+'classes_ridgeFR120200119.csv',inpath_table+'classes_ridgeA120200117.csv']
    
    if dt=='20200112':
        #20200112T034138_20200116T034200
        
        #2020-01-12 03:41:00,109.99937125251066,87.26208996286708,298.75119555621717,5.8614527134766465,2.1244788899482194
        lon0=109.99937125251066
        lat0=87.26208996286708
        head0=298.75119555621717
        
        rug_fn = [inpath_table+'classes_Sloop20200116.csv',inpath_table+'classes_Nloop20200116.csv',inpath_table+'classes_runway20200112.csv',inpath_table+'classes_snow120200112.csv',inpath_table+'classes_recon20200107.csv',inpath_table+'classes_special20200107.csv',inpath_table+'classes_special20200115.csv',inpath_table+'classes_special20200123.csv',inpath_table+'classes_recon20200126.csv',inpath_table+'classes_special20200126.csv',inpath_table+'classes_ridgeFR120200119.csv',inpath_table+'classes_ridgeA120200117.csv']

    if dt=='20200213':
        #20200213T055044_20200216T055106
        #2020-02-13 05:50:00,85.15144901470352,87.94738928916001,276.682326681203,4.456229160783077,0.9302815730387157
        lon0=85.15144901470352
        lat0=87.94738928916001
        head0=276.682326681203
        
        rug_fn = [inpath_table+'classes_Sloop20200220.csv',inpath_table+'classes_Nloop20200220.csv',inpath_table+'classes_runway20200207.csv',inpath_table+'classes_snow120200207.csv',inpath_table+'classes_ridgeFR120200221.csv',inpath_table+'classes_ridgeFR220200221.csv',inpath_table+'classes_ridgeA120200228.csv',inpath_table+'classes_recon20200228.csv',inpath_table+'classes_recon20200226.csv']

    if dt=='20200317':
        #20200317T095226_20200317T095248
        #2020-03-17 09:52:00,12.362527398569497,86.78831010296078,200.224132058465,3.7297813713179213,0.89337834329511
        lon0=12.362527398569497
        lat0=86.78831010296078
        head0=200.224132058465
        
        rug_fn = [inpath_table+'classes_Sloop20200330.csv',inpath_table+'classes_Nloop20200326.csv']
        
    if dt=='20200328':
        #20200328T112657_20200328T112719
        #2020-03-28 11:27:00,13.270078611108508,85.5951255232772,196.48183819244613,8.66019779558356,2.614077980232676
        lon0=13.270078611108508
        lat0=85.5951255232772
        head0=196.48183819244613
        
        rug_fn = [inpath_table+'classes_Sloop20200330.csv',inpath_table+'classes_Nloop20200326.csv']
    
    arr1,rot_x1,rot_y1=proj_sat(fn1,lon0,lat0,head0,alos=False,spacing=1,band=1,ps_pos=True)
    
    #manual position corrections
    if dt=='20191005':       
        rot_x1 = rot_x1+9300
        rot_y1 = rot_y1+2100
    
    if dt=='20191016':
        rot_x1 = rot_x1-800
        rot_y1 = rot_y1-300
        
    if dt=='20191031':
        rot_x1 = rot_x1+50
        rot_y1 = rot_y1+50
    
    if dt=='20191115':
        rot_x1 = rot_x1+40
        rot_y1 = rot_y1+40
        
    if dt=='20191215':
        #original
        rot_x1 = rot_x1+60
        rot_y1 = rot_y1+40
        ##gridded
        #rot_x1 = rot_x1+50
        #rot_y1 = rot_y1+50
        
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
        #original
        rot_x1 = rot_x1+10
        rot_y1 = rot_y1-40
        ##gridded
        #rot_x1 = rot_x1+0
        #rot_y1 = rot_y1+40
        
    #Wenkai writes missing values as 999
    arr1 = np.ma.array(arr1,mask=arr1==999)

    #setup figure
    fig1 = plt.figure(figsize=(20,10))
    
    ax = fig1.add_subplot(111)
    CS1=ax.contourf(rot_x1, rot_y1, arr1.T, 50,cmap=plt.cm.binary_r)
    #cb = plt.colorbar(CS1)  # draw colorbar
    #cb.set_label(label='Intensity (dB)',fontsize=20)

    #limit the region
    ax.set_xlim(-1500,2000)
    ax.set_ylim(-1000,1000)
    
    
    #ax.set_xlim(-10000,10000)
    #ax.set_ylim(-10000,10000)

    #larger ticks
    ax.tick_params(axis="x", labelsize=18)
    ax.tick_params(axis="y", labelsize=18)
    
    #start roughness scatter plot
    fig2 = plt.figure(figsize=(10,10))
    cx = fig2.add_subplot(111)
    
    #mask arrays
    data=arr1.T; del arr1
    rot_x1=np.ma.array(rot_x1,mask=data.mask).compressed()
    rot_y1=np.ma.array(rot_y1,mask=data.mask).compressed()
    data=data.compressed()
    
    #plot some transect data
    x_data_dt=[]
    y_data_dt=[]
    
    for fname in rug_fn:
        print(fname)

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
        
        it = cc/ii
        
        
        
        

        #some positioning adjustment for Sloop in March
        loc=fname.split('_')[-1].split('20')[0]
        if (loc=='Sloop') & (dt=='20200317'):
            xx = xx-210
            yy = yy+280
        
        if (loc=='Sloop') & (dt=='20200328'):
            xx = xx-130
            yy = yy+100

        #ice thickness
        chart = ax.scatter(xx,yy,c=it,s=5,cmap=plt.cm.Reds,vmin=0,vmax=1)
        
        if scatter:
            #get smooting window size/sampling interval - here we use X pixel size: ~positioning error + ~roughness feature size
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
            xx = xx[::window]
            yy = yy[::window]
            std = std[::window]        

            #only repeated/gridded transects
            if loc in ['Nloop','Sloop','runway','snow1']:#,'recon','special']:
                hh_mean=[]
                for i in range(0,len(xx)):
                    dx = xx[i]-rot_x1
                    dy = yy[i]-rot_y1
                    d = np.sqrt(dx**2+dy**2)
                    
                    ##take average a window (closest pixels)
                    hh_mean.append(np.mean(data[np.argsort(np.abs(d))[:intensity_window]]))
                
                #plot roughness vs mean window intensity
                if loc=='Nloop': color='salmon'
                if loc=='Sloop': color='purple'
                if loc=='snow1': color='gold'
                if loc=='runway': color='pink'
                if loc=='special': color='c'
                if loc=='recon': color='darkred'

                cx.scatter(std,hh_mean,c=color,label=loc)
                if dt=='20200112':
                    ccx.scatter(std,hh_mean,c=color,alpha=.5,label=loc)
                else:
                    ccx.scatter(std,hh_mean,c=color,alpha=.5)
                
                #store the data points
                x_data_dt.extend(std)
                y_data_dt.extend(hh_mean)
                x_data.extend(std)
                y_data.extend(hh_mean)
                
                del hh_mean,std,xx,yy,dx,dy,d
                
    cb = plt.colorbar(chart, ax=ax, pad=.01)
    cb.set_label(label='Consolidation %',fontsize=20)
    cb.ax.tick_params(labelsize=20)
    
    
    plt.show()
    fig1.savefig(outpath+outname,bbox_inches='tight')
    plt.close(fig1)
    
    del rot_x1,rot_y1


        
 






        
#
