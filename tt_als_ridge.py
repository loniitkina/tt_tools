import numpy as np
from osgeo import gdal, osr
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from datetime import datetime
from glob import glob
from tt_func import getColumn, proj_sat
import gc


#reference heading in Floenavi: 301.63560882616076

outpath='../data/ridges/'


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
outname='ALS_20200121_ridge_transects.png'
#outname='ALS_20200121_Sloop.png'


#refstation
#2020-01-21 10:35:00,96.16950957480864,87.48817329565784,284.55644100627484,3.348816529475723,0.686339670008361
lon0=96.16950957480864
lat0=87.48817329565784
head0=284.55644100627484

arr,rot_x,rot_y=proj_sat(tif,lon0,lat0,head0,spacing=4,band=1,alos=False)

#setup figure
fig1 = plt.figure(figsize=(20,10))

ax = fig1.add_subplot(111)
CS1=ax.contourf(rot_x, rot_y, arr.T, 50,cmap=plt.cm.binary_r)
#cb = plt.colorbar(CS1)  # draw colorbar
#cb.set_label(label='Intensity (dB)',fontsize=20)

#limit the region
ax.set_xlim(100,900)
ax.set_ylim(-600,0)

#prepare data for search
data=arr.T.flatten()
rot_x=rot_x.flatten()
rot_y=rot_y.flatten()

#magnaprobe transects
inpath_table = '../data/MCS/MP/'
flist = glob(inpath_table+'*/magna+gem2-transect-'+'*ridgeFR[1-3]*.csv')
flist.sort()

for i in range(0,len(flist)):
    
    elev=[]
    
    fname = flist[i]
    print(fname)
    date = fname.split('-')[-3].split('_')[0]
    print(date)
    loc = fname.split('_')[-1].split('.')[0]
    print(loc)

    xx = getColumn(fname,3, delimiter=',')
    xx = np.array(xx,dtype=np.float)
    
    yy = getColumn(fname,4, delimiter=',')
    yy = np.array(yy,dtype=np.float)
    
    it = getColumn(fname,6, delimiter=',')
    it = np.array(it,dtype=np.float)
    
    #some coordinate adjustments
    
    
    ax.scatter(xx,yy,c=it,s=5,cmap=plt.cm.Reds,vmin=0,vmax=5)

    #get closest values in ALS array
    for j in range(0,len(xx)):
        dx = xx[j]-rot_x
        dy = yy[j]-rot_y
        d = np.sqrt(dx**2+dy**2)
        
        #closest in ALS array
        elev.append(data[np.argmin(np.abs(d))])
        
    #print(elev)
    #plt.plot(elev)
    #plt.show()
    
    #write file
    tt = [xx,yy,elev]
    table = list(zip(*tt))

    file_name=outpath+fname.split('/')[-1].split('.csv')[0]+'_ALS.csv'
    print(file_name)
    with open(file_name, 'wb') as f:
        #header
        f.write(b'x,y,ALS elevation (m)\n')
        np.savetxt(f, table, fmt="%s", delimiter=",")

    
fig1.savefig(outpath+outname,bbox_inches='tight')
plt.close(fig1)
    
            

        

            
