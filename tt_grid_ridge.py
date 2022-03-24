import numpy as np
from glob import glob
from tt_func import getColumn, ridge_thick, ridge_xy
from scipy.signal import savgol_filter
from scipy.interpolate import griddata
import matplotlib.pyplot as plt

#bad data following headers deleted in thickness and track files ahead of procesing here?


#grid parameters
step = 1        #for ridges
limit = step*2  #how far from MP coordinate to search 
method_gem2 = 'nearest'
method_mp = 'nearest'   #at dense grids every measurement should be used separately

table_output=True

#location - ridges
#loc = 'ridgeFR1'    #installation (also very close to snow)
#date = '20200108'
#date = '20200119'
#date = '20200221'
#date = '20200305'   #not a point measurement, use tt_grid.py


#loc = 'ridgeFR2'    #coring
#date = '20200110'
#date = '20200212'
#date = '20200221'


loc = 'ridgeFR3'    #optics
date = '20200131'   #only one GEM2 transect, but 9 holes drilled!!!

#loc = 'ridgeA1'    #central
#date = '20200117'                  #good data in all channels
#date = '20200131'                #a lot of nans at the crest in all but highest channels
#date = '20200228'               #full of nans except in the first channel and 63q


#loc = 'ridgeA2'    #north
#date = '20200212'
#date = '20200228'


#loc = 'ridgeA3'    #south
#date = '20200212'
#date = '20200228'

#leg 4 Allie's Ridge
loc = 'ridge'
date = '20200628'
date = '20200709' #MP and GEM-2 data quite shifted, bad coordinate match
date = '20200713'   #GPS failure on two out of three GEM-lines
date = '20200721'   #no MP data found
date = '20200728'   #just one line, strange GEM-2 coordinates.




#examples of dates when there is something wrong with the GEM-2 data
if date == '20200119' and loc=='ridgeFR1':  #GEM-2 was not used
    date_gem2 = '20200108'    
elif date == '20200221' and loc=='ridgeFR2':  #GEM-2 was not used 
    date_gem2 = '20200212' 
else:
    date_gem2 = date

print(loc)
print(date)
print(date_gem2)

outpath = '../plots_AGU/'
outpath_grid = '../data/grids_AGU/'

#MP
#inpath_snow = '../../../MOSAiC/leg2_ICE/transect/'
inpath_snow = '../data/MCS/MP/'

#GEM-2
#inpath_ice = '../../../MOSAiC/thickness_workspace/01-ice-thickness/'
inpath_ice = '../data/MCS/GEM2_thickness/01-ice-thickness/'

#coordinates
fname = glob(inpath_ice+date_gem2+'*/mosaic-*-*-gem2-*-track-icecs-xy.csv')[0]
if date=='20200628':
    fname = glob(inpath_ice+date_gem2+'*/mosaic-*-*-gem2-*-track-icecs-xy.csv')[1]
print(fname)

xx,yy=ridge_xy(fname)   

#ice thickness data
fname = glob(inpath_ice+date_gem2+'*/mosaic-*-*-gem2-*-channel-thickness.csv')[0]
if date=='20200628':
    fname = glob(inpath_ice+date_gem2+'*/mosaic-*-*-gem2-*-channel-thickness.csv')[1]
print(fname)

mit1,mit2,mit3,mit4,mit5,mit6,mit7,mit8,mit9,mit10=ridge_thick(fname)

#MP
fname = glob(inpath_snow+'*/magnaprobe-transect-'+date+'*'+loc+'-track-icecs-xy_corr.csv')[0]
print(fname)

dt = getColumn(fname,0)
lon = getColumn(fname,1)
lat = getColumn(fname,2)

mxx = getColumn(fname,3)
mxx = np.array(mxx,dtype=np.float)

myy = getColumn(fname,4)
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
snod = getColumn(fname,3, delimiter=',', skipheader=4)
snod = np.array(snod,dtype=np.float)[:-2]/100             #convert from cm to m
#change all negative data to zero
snod = np.where(snod<0,0,snod)
    
#####################################################################################################################################3
#lets make a regular grid with 'step' m spacing, corresponding to the CO local coordinate boundaries
grid_x, grid_y = np.mgrid[200:900:step, -600:0:step]
extent=(200,900,-600,0)

#leg 4 data has different coordinates
if date=='20200628':
    grid_x, grid_y = np.mgrid[-450:-350:step, -600:-500:step]
    extent=(-450,-350,-600,-500)


#assign values to be used for gridding
sd_points = np.column_stack((mxx,myy))

sd_values = snod[1:]

if date=='20200119':
    sd_values = snod

print(sd_points.shape)
print(sd_values.shape)

#interpolate the data to regular grid
grid_sd = griddata(sd_points, sd_values, (grid_x, grid_y), method=method_mp)       

#run through all the grid and identify all the grid cells that are actually close enough to the data
mask_g = np.ones_like(grid_x)

for m in range(0,grid_x.shape[0]):
    for n in range(0,grid_x.shape[1]):
        dx = mxx-grid_x[m,n]
        dy = myy-grid_y[m,n]                    
        dg = np.sqrt(dx**2+dy**2)
        
        if np.min(dg) < limit: mask_g[m,n]=0

#total thickness data
channels = [mit1,mit2,mit3,mit4,mit5,mit6,mit7,mit8,mit9,mit10]
ch_name =  ['_f1525Hz_hcp_i','_f1525Hz_hcp_q', '_f5325Hz_hcp_i', '_f5325Hz_hcp_q', '_f18325Hz_hcp_i', '_f18325Hz_hcp_q', '_f63025Hz_hcp_i', '_f63025Hz_hcp_q', '_f93075Hz_hcp_i','_f93075Hz_hcp_q']
grid_mit1=[];grid_mit2=[];grid_mit3=[];grid_mit4=[];grid_mit5=[];grid_mit6=[];grid_mit7=[];grid_mit8=[];grid_mit9=[];grid_mit10=[]
output_tt = [grid_mit1,grid_mit2,grid_mit3,grid_mit4,grid_mit5,grid_mit6,grid_mit7,grid_mit8,grid_mit9,grid_mit10]

for ch in range(0,len(channels)):
    points = np.column_stack((xx,yy))
    values = np.array(channels[ch])
    
    print(points.shape)
    print(values.shape)
    
    grid_tt = griddata(points, values, (grid_x, grid_y), method=method_gem2)

    #difference = sea ice thickness
    grid_it = grid_tt - grid_sd

    #keep the original grid for nn search later
    output_tt[ch] = grid_tt.copy()

    #ensure that we have data for exactly same grid points
    data_mask = (np.isnan(grid_sd)) | (np.isnan(grid_tt)) | (mask_g == 1)
    grid_sd1 = np.ma.array(grid_sd,mask=data_mask).filled(np.nan)           #use a fresh copy for every channel of nans are going to be carried on...
    grid_tt = np.ma.array(grid_tt,mask=data_mask).filled(np.nan)
    grid_it = np.ma.array(grid_it,mask=data_mask).filled(np.nan)

    ##lets check how this looks like
    plt.subplot(221)
    plt.imshow(mask_g.T, extent=extent, origin='lower')
    plt.title('Original')
    plt.subplot(222)
    plt.imshow(grid_sd1.T, extent=extent, origin='lower',vmin=0,vmax=.5, cmap=plt.cm.Spectral_r)
    plt.colorbar()
    plt.title('Snow')
    plt.subplot(223)
    plt.imshow(grid_tt.T, extent=extent, origin='lower',vmin=0,vmax=4, cmap=plt.cm.Spectral_r)
    plt.colorbar()
    plt.title('Total')
    plt.subplot(224)
    plt.imshow(grid_it.T, extent=extent, origin='lower',vmin=0,vmax=4, cmap=plt.cm.Spectral_r)
    plt.colorbar()
    plt.title('Ice')
    plt.gcf().set_size_inches(6, 6)
    plt.show()

    #save all these gridded data
    stp = str(step)
    #of = outpath_grid+loc+'_'+date+'_'+stp+'m.npz'
    of = outpath_grid+loc+'_'+date+'_'+stp+'m_'+method_gem2+ch_name[ch]+'.npz'
    #if (date_gem2 == '20200223') or (date_gem2 == '20191226' and loc=='Nloop'):
        #of = outpath_grid+loc+'_'+date_gem2+'_'+stp+'m_'+method_gem2+'.npz'
    print(of)
    with open(of, 'wb') as f:
        np.savez(f, x = grid_x, y = grid_y, snow = grid_sd1, tt = grid_tt, ice = grid_it)

##########################################################################################################
if table_output==True:
    #write out the ice mass balance transect collocated tables
    
    #create output name
    outname = fname.split('probe')[0]+'+gem2'+fname.split('probe')[1].split('.dat')[0]+'.csv'
    
    #if (date_gem2 == '20200223') or (date_gem2 == '20191226' and loc=='Nloop'):
        #outname = fname.split('probe')[0]+'+gem2'+fname.split('probe')[1].split('.dat')[0]+'_ice_from_'+date_gem2+'.csv'


    tt_nn1 = np.zeros_like(sd_values)
    tt_nn2 = np.zeros_like(sd_values)
    tt_nn3 = np.zeros_like(sd_values)
    tt_nn4 = np.zeros_like(sd_values)
    tt_nn5 = np.zeros_like(sd_values)
    tt_nn6 = np.zeros_like(sd_values)
    tt_nn7 = np.zeros_like(sd_values)
    tt_nn8 = np.zeros_like(sd_values)
    tt_nn9 = np.zeros_like(sd_values)
    tt_nn10 = np.zeros_like(sd_values)    
    
    #find nearest tt and it values to original mp/sd points        
    for i in range(0,sd_values.shape[0]):
        dx = sd_points[:,0][i]-grid_x
        dy = sd_points[:,1][i]-grid_y                  
        dg = np.sqrt(dx**2+dy**2)
        
        #find nearest tt and it value
        dgf = dg.flatten()
        nn = np.argmin(dgf)
        
        tt_nn1[i] = output_tt[0].flatten()[nn]
        tt_nn2[i] = output_tt[1].flatten()[nn]
        tt_nn3[i] = output_tt[2].flatten()[nn]
        tt_nn4[i] = output_tt[3].flatten()[nn]
        tt_nn5[i] = output_tt[4].flatten()[nn]
        tt_nn6[i] = output_tt[5].flatten()[nn]
        tt_nn7[i] = output_tt[6].flatten()[nn]
        tt_nn8[i] = output_tt[7].flatten()[nn]
        tt_nn9[i] = output_tt[8].flatten()[nn]
        tt_nn10[i] = output_tt[9].flatten()[nn]        
        
       
    it_nn1 = tt_nn1 - sd_values
    it_nn2 = tt_nn2 - sd_values
    it_nn3 = tt_nn3 - sd_values
    it_nn4 = tt_nn4 - sd_values
    it_nn5 = tt_nn5 - sd_values
    it_nn6 = tt_nn6 - sd_values
    it_nn7 = tt_nn7 - sd_values
    it_nn8 = tt_nn8 - sd_values
    it_nn9 = tt_nn9 - sd_values
    it_nn10 = tt_nn10 - sd_values    
    
    #write new csv file with all the ice mass balance variables
    tt = [dt,lon,lat,sd_points[:,0],sd_points[:,1],sd_values,it_nn1,it_nn2,it_nn3,it_nn4,it_nn5,it_nn6,it_nn7,it_nn8,it_nn9,it_nn10]
    table = list(zip(*tt))

    print(outname)
    with open(outname, 'wb') as f:
        #header
        f.write(b'Date/Time, Lon, Lat, Local X, Local Y, Snow Depth (m), Ice Thickness f1525Hz_hcp_i (m), Ice Thickness f1525Hz_hcp_q (m) Ice Thickness f5325Hz_hcp_i (m), Ice Thickness f5325Hz_hcp_q (m), Ice Thickness f18325Hz_hcp_i (m), Ice Thickness f18325Hz_hcp_q (m), Ice Thickness f63025Hz_hcp_i (m),Ice Thickness f63025Hz_hcp_q (m), Ice Thickness f93075Hz_hcp_i (m), Ice Thickness f93075Hz_hcp_q (m)\n')
        np.savetxt(f, table, fmt="%s", delimiter=",")

