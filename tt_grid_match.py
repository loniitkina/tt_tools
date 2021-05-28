import numpy as np
from glob import glob
from tt_func import getColumn, semivar, polymodel
from scipy import ndimage
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


step = 2        #grid spacing in meters 
stp = str(step)
method_gem2 = 'nearest'
#method_gem2 = 'linear'
ch_name = '_18kHz'

#location and dates
loc = 'Sloop'
dates = ['20191031','20191107','20191114','20191205',   '20200102','20200109','20200116','20200130','20200206','20200220','20200227','20200305','20200330','20200426','20200507']    #best data

inpath_grid = '../data/grids_AGU/'

#set up plot
extent=(-950,850,-600,620)
plt.subplot(111)
plt.title('Ice')
plt.gcf().set_size_inches(6, 6)

for dd in range(0,len(dates)):
    date = dates[dd]
    print(date)
    
    #load data
    of = inpath_grid+loc+'_'+date+'_'+stp+'m_'+method_gem2+ch_name+'.npz'
    #of = inpath_grid+loc+'_'+date+'_'+stp+'m_'+method_gem2+'.npz'
    data = np.load(of)

    x_grid = data['x']
    y_grid = data['y']
    s_grid = data['snow']
    i_grid = data['ice']

    #print(i_grid)
    print(i_grid.shape)
    
    #move along y axis
    if date == '20191031' or date == '20191107' or date == '20191114':
        i_grid = np.append(i_grid[:,-49:],i_grid[:,:-49],axis=1)            #this is same as numpy.roll
        s_grid = np.append(s_grid[:,-49:],s_grid[:,:-49],axis=1)
        
    if date == '20200330' or date == '20200426' or date == '20200507':
        i_grid = np.append(i_grid[:,-245:],i_grid[:,:-245],axis=1)
        s_grid = np.append(s_grid[:,-245:],s_grid[:,:-245],axis=1)
                
    #move along x axis
    if date == '20191031' or date == '20191107' or date == '20191114':
        i_grid = np.append(i_grid[212:,:],i_grid[:212,:],axis=0) 
        s_grid = np.append(s_grid[212:,:],s_grid[:212,:],axis=0)
        
    if date == '20200102':
        i_grid = np.append(i_grid[-20:,:],i_grid[:-20,:],axis=0)
        s_grid = np.append(s_grid[-20:,:],s_grid[:-20,:],axis=0)
        
    if date == '20200109':
         i_grid = np.append(i_grid[-10:,:],i_grid[:-10,:],axis=0)
         s_grid = np.append(s_grid[-10:,:],s_grid[:-10,:],axis=0)
    
    if date == '20200116':
        i_grid = np.append(i_grid[-13:,:],i_grid[:-13,:],axis=0)
        s_grid = np.append(s_grid[-13:,:],s_grid[:-13,:],axis=0)
    
    if date == '20200206' or date == '20200220' or date == '20200227' or date == '20200305':
        i_grid = np.append(i_grid[-5:,:],i_grid[:-5,:],axis=0)
        s_grid = np.append(s_grid[-5:,:],s_grid[:-5,:],axis=0)
        
    if date == '20200330' or date == '20200426' or date == '20200507':
        i_grid = np.append(i_grid[-125:,:],i_grid[:-125,:],axis=0)
        s_grid = np.append(s_grid[-125:,:],s_grid[:-125,:],axis=0)
        
    #rotate
    if date == '20200330' or date == '20200426' or date == '20200507':
        i_grid = ndimage.rotate(i_grid, 1, reshape=False)   #rotate by 1 degree
        s_grid = ndimage.rotate(s_grid, 1, reshape=False)
        
    print(i_grid.shape)
    
    #lets check how this looks like
    plt.imshow(s_grid.T, extent=extent, origin='lower',vmin=0,vmax=5)
    
    #save new grids
    ofn = inpath_grid+loc+'_'+date+'_'+stp+'m_'+method_gem2+ch_name+'_adjusted.npz'
    
    with open(ofn, 'wb') as f:
        np.savez(f, x = x_grid, y = y_grid, snow = s_grid, ice = i_grid)

    
plt.show()
