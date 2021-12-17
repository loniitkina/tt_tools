import numpy as np
from glob import glob
from tt_func import getColumn, semivar, polymodel
from scipy import ndimage
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


step = 1        #grid spacing in meters 
stp = str(step)
method_gem2 = 'nearest'
#method_gem2 = 'linear'
ch_name = '_18kHz'


locs = ['Sloop']
##dates = [ ['20191031','20191107','20191114','20191205',   '20191226','20200102','20200109','20200116','20200130','20200206','20200220','20200227','20200305','20200330','20200406','20200426','20200507'] ]

dates = [ ['20200116','20200507'] ]



inpath_grid = '../data/grids_AGU/'
outpath = '../plots_AGU/'
outname='grid_test.png'
#outname = 'grid_maps3.png'
#outname = 'grid_maps_legs1-4.png'
#outname2 = 'map_legs1-4.png'

print(outpath+outname)

#set up plot
#extent=(-950,850,-600,620) #old
extent=(-950,820,-1200,650) #extended
fig1 = plt.figure(figsize=(40,50))
ax = fig1.add_subplot(131)
ax.set_title('Original')
bx = fig1.add_subplot(132)
bx.set_title('Shifted and Rotated')
cx = fig1.add_subplot(133)
cx.set_title('De-deformed')


for ll in range(0,len(locs)):
    print(locs[ll])
    
    for dd in range(0,len(dates[ll])):
        date = dates[ll][dd]
        print(date)
        
        #load data
        of = inpath_grid+locs[ll]+'_'+date+'_'+stp+'m_'+method_gem2+ch_name+'.npz'
        #of = inpath_grid+loc+'_'+date+'_'+stp+'m_'+method_gem2+'.npz'
        print(of)
        
        data = np.load(of)

        x_grid = data['x']
        y_grid = data['y']
        s_grid = data['snow']
        i_grid = data['ice']
        
        del data
        
        #lets check how this looks like before the shifting and rotation
        if dd == 0:
            i_grid1 = np.ma.masked_invalid(s_grid).filled(0)
            
            i_grid2=i_grid1.copy()
            i_grid3=i_grid1.copy()
            
        else:
             i_grid1 = i_grid1+np.ma.masked_invalid(s_grid).filled(0)
        
        #get rid of nans for the operations
        i_grid=np.ma.masked_invalid(i_grid).filled(-999)
        s_grid=np.ma.masked_invalid(s_grid).filled(-999)
        
        #fit to the reference date
        
        if locs[ll]=='Sloop':
                
            if date == '20200507':
                i_grid = np.append(i_grid[:,int(-470/step):],i_grid[:,:int(-470/step)],axis=1)
                s_grid = np.append(s_grid[:,int(-470/step):],s_grid[:,:int(-470/step)],axis=1)    
                        
            #move along x axis
                
            if date == '20200507':
                i_grid = np.append(i_grid[int(-240/step):,:],i_grid[:int(-240/step),:],axis=0)
                s_grid = np.append(s_grid[int(-240/step):,:],s_grid[:int(-240/step),:],axis=0)
            
            #rotate
            #chose order=1 for no interpolation at boundaries!
            #chose mode='nearest' to have no boundary effect!
                
            if date == '20200507':
                i_grid = ndimage.rotate(i_grid, 4.5, reshape=False,order=0,mode='nearest')
                s_grid = ndimage.rotate(s_grid, 4.5, reshape=False,order=0,mode='nearest')
            
            #check how it looks like after the lateral shifts
            tmpi = np.ma.array(i_grid,mask=i_grid<0).filled(np.nan)
            if dd == 0:
                i_grid2 = np.ma.masked_invalid(tmpi).filled(0)
            else:
                i_grid2 = i_grid2+np.ma.masked_invalid(tmpi).filled(0)
            del tmpi
            
            
            
        
        i_grid = np.ma.array(i_grid,mask=i_grid<0).filled(np.nan)
        s_grid = np.ma.array(s_grid,mask=s_grid<0).filled(np.nan)
        
        #lets check how this looks like after the adjusting
        if dd == 0:
            i_grid3 = np.ma.masked_invalid(s_grid).filled(0)
        else:
            i_grid3 = i_grid3+np.ma.masked_invalid(s_grid).filled(0)
        
        #save new grids
        ofn = inpath_grid+locs[ll]+'_'+date+'_'+stp+'m_'+method_gem2+ch_name+'_adjusted.npz'
        print(ofn)
        
        with open(ofn, 'wb') as f:
            np.savez(f, x = x_grid, y = y_grid, snow = s_grid, ice = i_grid)
        f.close()    
        
        #check if the sizes of both grids match
        print(np.ma.masked_invalid(i_grid).compressed().shape)
        print(np.ma.masked_invalid(s_grid).compressed().shape)
        
        

    #get the transparency for the plots
    i_grid1 = np.ma.array(i_grid1,mask=i_grid1==0).filled(np.nan)
    i_grid2 = np.ma.array(i_grid2,mask=i_grid2==0).filled(np.nan)
    i_grid3 = np.ma.array(i_grid3,mask=i_grid3==0).filled(np.nan)

    ax.imshow(i_grid1.T, extent=extent, origin='lower',vmin=0,vmax=3)
    bx.imshow(i_grid2.T, extent=extent, origin='lower',vmin=0,vmax=3)
    cx.imshow(i_grid3.T, extent=extent, origin='lower',vmin=0,vmax=3)
    
    
plt.show()    
#fig1.savefig(outpath+outname,bbox_inches='tight')

