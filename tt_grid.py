import numpy as np
from glob import glob
from tt_func import getColumn
from scipy.interpolate import griddata
import matplotlib.pyplot as plt

#grid parameters
step = 5        #grid spacing in meters 
limit = step*2  #how far from MP coordinate to search (for mask)


#location
loc = 'Nloop'
date = '20191107'
date = '20191114'
date = '20191205'
date = '20191219'
date = '20200102'
date = '20200109'
#date = '20200130'
#date = '20200206'
#date = '20200220'
#date = '20200227'
#date = '20200305'
#date = '20200416'   #no GPS coordinates from GEM-2
#date = '20200430'   #this is not Nloop ice!!!

#loc = 'Sloop'
#date = '20191107'
#date = '20191114'
#date = '20191205'
#date = '20191226'
#date = '20200102'
#date = '20200109'
#date = '20200130'
#date = '20200206'
#date = '20200220'
#date = '20200227'
#date = '20200305'
#date = '20200330'
#date = '20200426'


##location
#loc = 'snow1'

#date
#date = '20191222'
#date = '20200112'
#date = '20200126'
#date = '20200207'

##location
#loc = 'ANJA_36_special'

##long transect
#date = '20200123'



print(date)
print(loc)

outpath = '../plots_AGU/'
outpath_grid = '../data/grids_AGU/'

#MP
#inpath_snow = '../../../MOSAiC/leg2_ICE/transect/'
inpath_snow = '../data/MCS/MP/'

#GEM-2
#inpath_ice = '../../../MOSAiC/thickness_workspace/01-ice-thickness/'
inpath_ice = '../data/MCS/GEM2_thickness/01-ice-thickness/'





#make file list for each location








#coordinates
fname = glob(inpath_ice+date+'*/mosaic-transect-*-gem2-556-track-icecs-xy.csv')[0]
print(fname)
xx = getColumn(fname,3, delimiter=',', magnaprobe=False)
xx = np.array(xx,dtype=np.float)

yy = getColumn(fname,4, delimiter=',', magnaprobe=False)
yy = np.array(yy,dtype=np.float)

#ice thickness data
fname = glob(inpath_ice+date+'*/mosaic-transect-*-gem2-556-channel-thickness.csv')[0]
#time, record_id, longitude, latitude, xc, yc, f1525Hz_hcp_i, f1525Hz_hcp_q, f5325Hz_hcp_i, f5325Hz_hcp_q, f18325Hz_hcp_i, f18325Hz_hcp_q, f63025Hz_hcp_i, f63025Hz_hcp_q, f93075Hz_hcp_i, f93075Hz_hcp_q
tt = getColumn(fname,10, delimiter=',', magnaprobe=False)        #take 18KHz
#if date == '20200123':                                          #this date needs to be recalibrated for highest freqnency, take another for now...
    #tt = getColumn(fname,7, delimiter=',', magnaprobe=False)

##Nloop data has problems at certain dtes in certain frequnecies
#if loc=='Nloop'
    #if date == '20191107':
        #tt = getColumn(fname,6, delimiter=',', magnaprobe=False)        #take 
    #if date == '20191114':
        #tt = getColumn(fname,6, delimiter=',', magnaprobe=False)

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
fname = glob(inpath_snow+'*/magnaprobe-transect-'+date+'*'+loc+'-track-icecs-xy_corr.csv')[0]
print(fname)

mxx = getColumn(fname,3, delimiter=',', magnaprobe=False)
mxx = np.array(mxx,dtype=np.float)

myy = getColumn(fname,4, delimiter=',', magnaprobe=False)
myy = np.array(myy,dtype=np.float)
    
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
fname = glob(inpath_snow+'*/magnaprobe-transect-'+date+'*'+loc+'.dat')[0]
print(fname)
snod = getColumn(fname,3, delimiter=',', magnaprobe=True)
snod = np.array(snod,dtype=np.float)[:-2]/100             #convert from cm to m
#print(mxx.shape)
#print(snod.shape)

#####################################################################################################################################3
#how do we grid the data to 1m grid???

#lets make a regular grid with 1 m spacing, corresponding to the CO local coordinate boundaries
grid_x, grid_y = np.mgrid[-950:820:step, -600:650:step]
extent=(-950,850,-600,620)

#long transect
if loc == 'ANJA_36_special':
    grid_x, grid_y = np.mgrid[2000:4500:step, 3000:6600:step]
    extent = (2000,4500,3000,6500)

points = np.column_stack((mxx,myy))
#print(points)

if loc == 'Sloop':
    if date=='20191107' or date == '20191114' or date == '20191205':
        values = snod
    else:
        values = snod[1:]   #something fishy here...
else:
    values = snod[1:]

print(snod.shape)
print(points.shape)


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

#in same ceses there will be no GEM-2 data - get at least gridded snow depth...
try:
    grid_z0_tt = griddata(points, values, (grid_x, grid_y), method='nearest')
    #grid_z0_tt = griddata(points, values, (grid_x, grid_y), method='linear')           #experimental option, unlikely - GEM-2 measurements are sub-second, nearest interpolation should be fine!!! NO - these measurements need to be smoothed!!!

    #grid_z0_tt = np.ma.array(grid_z0_tt,mask=mask_g).filled(np.nan)
except:
    grid_z0_tt = grid_z0

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

