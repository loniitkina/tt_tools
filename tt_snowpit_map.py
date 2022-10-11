import numpy as np
from osgeo import gdal, osr
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from datetime import datetime
from glob import glob
from tt_func import getColumn, proj_sat
import gc

outpath='../plots_sm/'

#RS-2 scene for 31 Dec 2019, 03:35:02 UTC
tif='../data/RS-2_Wenkai/RS2_20191231_033502_0004_FQ20W_HHVVHVVH_SLC_783865_1107_32077288_HV.tif'
outname='RS2_20191231_map_snowpits_selection1.png'
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

arr,rot_x,rot_y=proj_sat(tif,lon0,lat0,head0,spacing=1,band=1,ps_pos=True)

#Wenkai masks no values as 999
arr = np.where(arr==999,0,arr)

#setup figure
fig1 = plt.figure(figsize=(20,10))
ax = fig1.add_subplot(111)

#RS-2
RS2=ax.contourf(rot_x, rot_y, arr.T, 50,cmap=plt.cm.binary_r)

#limit the region
ax.set_xlim(-1500,2000)
ax.set_ylim(-1000,1000)

#larger ticks
ax.tick_params(axis="x", labelsize=18)
ax.tick_params(axis="y", labelsize=18)

del arr, rot_x, rot_y
gc.collect()


#Transects
inpath_table = '../data/MCS/MP/'
flist = glob(inpath_table+'*/magna+gem2-transect-'+'*.csv')
flist.sort()

locs=['Nloop','Sloop','runway']
dates=['20200116','20200112']


for i in range(0,len(flist)):
    
    fname = flist[i]
    print(fname)
    date = fname.split('-')[-3].split('_')[0]
    print(date)
    loc = fname.split('_')[-1].split('.')[0]
    print(loc)
    
    if loc in locs:
        if date in dates:

            xx = getColumn(fname,3, delimiter=',')
            xx = np.array(xx,dtype=np.float)
            
            yy = getColumn(fname,4, delimiter=',')
            yy = np.array(yy,dtype=np.float)
            
            it = getColumn(fname,9, delimiter=',')
            it = np.array(it,dtype=np.float)

            #GEM-2 files contain nans and zeros
            xx = np.ma.masked_invalid(xx).compressed()
            yy = np.ma.masked_invalid(yy).compressed()
            
            xx = np.ma.array(xx,mask=xx==0).compressed()
            yy = np.ma.array(yy,mask=yy==0).compressed()
    
            ax.scatter(xx,yy,c=it,s=5,cmap=plt.cm.Reds,vmin=0,vmax=5)
    
        
            del xx,yy,it
 
 
#and from CO2
from scipy import ndimage
inpath_grid = '../data/grids_AGU/'
loc='transect'
date='20200630'
stp='1'
method_gem2='nearest'
ch_name='_18kHz'


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
track = np.where(i_grid>0,1,0)

##plot
xx=np.ma.array(x_grid,mask=track==0).compressed().flatten()
yy=np.ma.array(y_grid,mask=track==0).compressed().flatten()
it=np.ma.array(i_grid,mask=track==0).compressed().flatten()

it_map=plt.scatter(xx,yy,c=it,s=5,cmap=plt.cm.Reds,vmin=0,vmax=5)

del xx,yy,x_grid,y_grid,i_grid
 
 
 
 
 
#snow pit locations
fnames = glob('../data/snowpits_wagner/swe_smpdensity_leg1_leg3_archive/plotting/swe_smp_k2020_*.csv')
selection = ['snow1-A1','snow1-A3','snow1-A5','runway1','RS-transect-north','snow1-transect']
cols = ['salmon','purple','gold','cornflowerblue','c','limegreen','salmon','deeppink','gold','salmon','purple','gold']


colors = plt.cm.rainbow(np.linspace(0, 1, len(fnames)))

for i in range(0,len(fnames)):
    fname = fnames[i]
    snowpit = fname.split('_')[-1].split('.csv')[0]
    print(snowpit)
    
    if snowpit in selection:
        
        x = getColumn(fname,6)
        x = np.array(x,dtype=np.float)
        y = getColumn(fname,7)
        y = np.array(y,dtype=np.float)

        ax.plot(x,y,'X',ms=5,c=cols[i],label=snowpit)

ax.legend()

cb = plt.colorbar(it_map, ax=ax, pad=.01)
cb.set_label(label='Sea ice thickness (m)',fontsize=20)
cb.ax.tick_params(labelsize=20)



fig1.savefig(outpath+outname,bbox_inches='tight')

