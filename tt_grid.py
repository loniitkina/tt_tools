import numpy as np
from glob import glob
from tt_func import getColumn
from scipy.interpolate import griddata
import matplotlib.pyplot as plt

#grid parameters
step = 1        #grid spacing in meters 
limit = step*2  #how far from MP coordinate to search (for mask)


#location
loc = 'Nloop'
loc = 'Sloop'
#date
#date = '20191219'
#date = '20191226'
#date = '20200102'
#date = '20200109'
#date = '20200130'
#date = '20200206'
#date = '20200220'

#location
loc = 'snow1'

#date
#date = '20191222'
date = '20200112'
#date = '20200126'
date = '20200207'

##location
#loc = 'ANJA_36_special'

##long transect
#date = '20200123'



print(date)
print(loc)

inpath = '../data/'
outpath = '../plots/'
outpath_grid = '../data/grids/'

#MP
inpath_snow = '../../../MOSAiC/leg2_ICE/transect/'

#GEM-2
inpath_ice = '../../../MOSAiC/thickness_workspace/01-ice-thickness/'

#coordinates
fname = glob(inpath_ice+date+'*/mosaic-transect-*-gem2-556-track-icecs-xy.csv')[0]
print(fname)
xx = getColumn(fname,3, delimiter=',', magnaprobe=False)
xx = np.array(xx,dtype=np.float)

yy = getColumn(fname,4, delimiter=',', magnaprobe=False)
yy = np.array(yy,dtype=np.float)

#ice thickness data
fname = glob(inpath_ice+date+'*/mosaic-transect-*-gem2-556-channel-thickness.csv')[0]
tt = getColumn(fname,6, delimiter=',', magnaprobe=False)
if date == '20200123':                                          #this date needs to be recalibrated for highest freqnency, take another for now...
    tt = getColumn(fname,7, delimiter=',', magnaprobe=False)

tt = np.array(tt,dtype=np.float)[1:-1]

#there can be nans in the thickness data, fix this before we proceed
tt = np.ma.masked_invalid(tt)
xx = xx[tt.mask == False]
yy = yy[tt.mask == False]
tt = tt[tt.mask == False]

#print(xx.shape)
#print(yy.shape)
#print(tt.shape)

#MP
fname = glob(inpath+date+'_*'+loc+'*_MP_transect_track-icecs-xy.csv')[0]
print(fname)
mxx = getColumn(fname,3, delimiter=',', magnaprobe=False)
mxx = np.array(mxx,dtype=np.float)

myy = getColumn(fname,4, delimiter=',', magnaprobe=False)
myy = np.array(myy,dtype=np.float)

##MP coordinates looks shifted to 'positive directions' - probably some drift in time between the GEM-2 and MP measurement???
##should the MP coordinates be manually corrected by some ~10 m???

#the corrections can be different for each date
#they are estimated manually, by overlaying MP and GEM-2 tracks. GEM-2 tracks are assumed to be of better quality.
#this corrections are copied from tt_track_overlay.py
if date == '20200220':
    mxx = mxx-10
    
    if loc == 'Nloop':
        myy = myy-3
    
if date == '20200102':
    mxx = mxx-7
    myy = myy-8
        
    if loc == 'Sloop':
        mxx = mxx+5
        
if date == '20200109':
    myy = myy-4  
    
if date == '20200126':
    myy = myy+7

if date == '20200130':
    mxx = mxx+3
    
if date == '20200206':
    mxx = mxx-5

#snow1
if date == '20191222':
    mxx = mxx+3
    myy = myy+3

#long transect (ice on 3 different groups of floes moving actively and independently)
if date == '20200123':
    print(len(mxx))
    mxx[:300] = mxx[:300]+15
    mxx[500:] = mxx[500:]-5
    
#get some meta data for the MP transect:
dx = mxx[1:]-mxx[:-1]
dy = myy[1:]-myy[:-1]
d = np.sum(np.sqrt(dx**2+dy**2))
print('transect length:')
print(d)
print('MP measurement spacing:')
spacing = np.mean(np.sqrt(dx**2+dy**2))
print(spacing)

of = fname.split('track')[0]+'meta.txt'
print(of)
np.savetxt(of, (d,spacing))

#snow depth data
flist = glob(inpath_snow+date+'/*'+loc+'.dat')
fname = flist[0]
print(fname)
snod = getColumn(fname,3, delimiter=',', magnaprobe=True)
snod = np.array(snod,dtype=np.float)[:-2]/100             #convert from cm to m
#print(mxx.shape)
#print(snod.shape)

#####################################################################################################################################3
#how do we grid the data to 1m grid???

#lets make a regular grid with 1 m spacing, corresponding to the CO local coordinate boundaries
grid_x, grid_y = np.mgrid[-500:700:step, -900:700:step]
extent=(-500,700,-900,700)

#long transect
if loc == 'ANJA_36_special':
    grid_x, grid_y = np.mgrid[2000:4500:step, 3000:6600:step]
    extent = (2000,4500,3000,6500)

points = np.column_stack((mxx,myy))
#print(points)

values = snod

grid_z0 = griddata(points, values, (grid_x, grid_y), method='nearest')
#grid_z0 = griddata(points, values, (grid_x, grid_y), method='linear')           #experimental option, potentially useful for the profile data - not for maps!!! (edges 'measurements belts' are influenced by no values)

#print(grid_z0)
#print(np.max(grid_z0))
#print(np.min(grid_z0))

#run through all the grid and identify all the grid cells that are actually close enough to the data
mask_g = np.ones_like(grid_x)

for m in range(0,grid_x.shape[0]):
    for n in range(0,grid_x.shape[1]):
        dx = mxx-grid_x[m,n]
        dy = myy-grid_y[m,n]                    
        dg = np.sqrt(dx**2+dy**2)
                
        if np.min(dg) < limit: mask_g[m,n]=0

## mask out the field
grid_z0 = np.ma.array(grid_z0,mask=mask_g).filled(np.nan)

##lets check how this looks like
#plt.subplot(221)
#plt.imshow(mask_g.T, extent=extent, origin='lower')
#plt.plot(points[:,0], points[:,1], 'k.', ms=1)
#plt.title('Original')
#plt.subplot(222)
#plt.imshow(grid_z0.T, extent=extent, origin='lower')
#plt.title('Nearest')
#plt.subplot(223)
#plt.imshow(grid_z1.T, extent=extent, origin='lower')
#plt.title('Linear')
#plt.subplot(224)
#plt.imshow(grid_z2.T, extent=extent, origin='lower')
#plt.title('Cubic')
#plt.gcf().set_size_inches(6, 6)
#plt.show()


#total thickness data
points = np.column_stack((xx,yy))
#print(points)

values = tt

grid_z0_tt = griddata(points, values, (grid_x, grid_y), method='nearest')
#grid_z0_tt = griddata(points, values, (grid_x, grid_y), method='linear')           #experimental option, unlikely - GEM-2 measurements are sub-second, nearest interpolation should be fine!!! NO - these measurements need to be smoothed!!!

#grid_z0_tt = np.ma.array(grid_z0_tt,mask=mask_g).filled(np.nan)

#difference = sea ice thickness
grid_z0_it = grid_z0_tt - grid_z0


##lets check how this looks like
plt.subplot(221)
plt.imshow(mask_g.T, extent=extent, origin='lower')
#plt.plot(points[:,0], points[:,1], 'k.', ms=1)
plt.title('Original')
plt.subplot(222)
plt.imshow(grid_z0.T, extent=extent, origin='lower',vmin=0,vmax=1.2, cmap=plt.cm.Reds)
plt.colorbar()
plt.title('Snow')
plt.subplot(223)
plt.imshow(grid_z0_tt.T, extent=extent, origin='lower',vmin=0,vmax=5, cmap=plt.cm.Reds)
plt.colorbar()
plt.title('Total')
plt.subplot(224)
plt.imshow(grid_z0_it.T, extent=extent, origin='lower',vmin=0,vmax=5, cmap=plt.cm.Reds)
plt.colorbar()
plt.title('Ice')
plt.gcf().set_size_inches(6, 6)
plt.show()

#save all these gridded data
stp = str(step)
of = outpath_grid+loc+'_'+date+'_'+stp+'m.npz'
#of = outpath_grid+loc+'_'+date+'_'+stp+'m_linear.npz'
print(of)
with open(of, 'wb') as f:
    np.savez(f, x = grid_x, y = grid_y, snow = grid_z0, tt = grid_z0_tt, ice = grid_z0_it)

