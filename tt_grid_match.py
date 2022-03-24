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

#location and dates
#selected reference date -to wich all other transects are centered - pick a date with good spacing and no detours etc!!!
#selected reference date: 20200116
locs = ['Sloop','Nloop']
dates = [['20191031','20191107','20191114','20191205',   '20191226','20200102','20200109','20200116','20200130','20200206','20200220','20200227','20200305','20200330','20200406','20200426','20200507'],
         
['20191024','20191031','20191107','20191114','20191121','20191128','20191205',  '20191219','20191226','20200102','20200109','20200116','20200130','20200206','20200220','20200227', '20200305','20200320','20200326','20200403','20200416','20200424','20200430','20200507']]

#locs = ['Sloop']
###dates = [ ['20191031','20191107','20191114','20191205',   '20191226','20200102','20200109','20200116','20200130','20200206','20200220','20200227','20200305','20200330','20200406','20200426','20200507'] ]

#selected reference date:20200207
#locs = ['snow1']
#dates = [['20191222','20200112','20200126','20200207','20200223','20200406']]

#selected reference date:20200207
#locs = ['runway']
#dates = [['20200112','20200207']]

###all leg1-4 transects on selected dates
#locs = ['Sloop','Nloop','snow1','runway','special','transect']
#dates = [['20200116'],
#['20200116'],
#['20200207'],
#['20200207'],
#['20200617'],
#['20200630']
#]


inpath_grid = '../data/grids_AGU/'
outpath = '../plots_AGU/'
outname='grid_method.png'
#outname = 'grid_maps3.png'
#outname = 'grid_maps_legs1-4.png'
#outname2 = 'map_legs1-4.png'

print(outpath+outname)

#set up plot
#extent=(-950,850,-600,620) #old
extent=(-950,820,-1200,650) #extended
fig1 = plt.figure(figsize=(20,40))  #for paper figure
#fig1 = plt.figure(figsize=(40,50)) #for checking alignment
ax = fig1.add_subplot(131)
#ax.set_title('a) Original', fontsize=20)
ax.text(-880, 550, "a", ha="center", va="center", size=25)  #make simple figure annotation
ax.tick_params(axis="x", labelsize=15)
ax.tick_params(axis="y", labelsize=15)
bx = fig1.add_subplot(132)
#bx.set_title('b) Shifted and Rotated', fontsize=20)
bx.text(-880, 550, "b", ha="center", va="center", size=25)
bx.tick_params(axis="x", labelsize=15)
bx.tick_params(axis="y", labelsize=15)
cx = fig1.add_subplot(133)
#cx.set_title('c) De-deformed', fontsize=20)
cx.text(-880, 550, "c", ha="center", va="center", size=25)
cx.tick_params(axis="x", labelsize=15)
cx.tick_params(axis="y", labelsize=15)

fig2 = plt.figure(figsize=(20,10))
dx = fig2.add_subplot(111)
dx.set_title('Final Map')

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
            i_grid1 = np.ma.masked_invalid(i_grid).filled(0)
            
            i_grid2=i_grid1.copy()
            i_grid3=i_grid1.copy()
            
        else:
             i_grid1 = i_grid1+np.ma.masked_invalid(i_grid).filled(0)
        
        #get rid of nans for the operations
        i_grid=np.ma.masked_invalid(i_grid).filled(-999)
        s_grid=np.ma.masked_invalid(s_grid).filled(-999)
        
        #fit to the reference date
        
        if locs[ll]=='Sloop':
            #move along y axis
            if date == '20191031' or date == '20191107' or date == '20191114':
                i_grid = np.append(i_grid[:,int(-66/step):],i_grid[:,:int(-66/step)],axis=1)            #this is same as numpy.roll
                s_grid = np.append(s_grid[:,int(-66/step):],s_grid[:,:int(-66/step)],axis=1)
                
            if date == '20191226':
                i_grid = np.append(i_grid[:,int(8/step):],i_grid[:,:int(8/step)],axis=1)
                s_grid = np.append(s_grid[:,int(8/step):],s_grid[:,:int(8/step)],axis=1)
                
            if date == '20200130':
                i_grid = np.append(i_grid[:,int(2/step):],i_grid[:,:int(2/step)],axis=1)
                s_grid = np.append(s_grid[:,int(2/step):],s_grid[:,:int(2/step)],axis=1)
                
            if date == '20200206':
                i_grid = np.append(i_grid[:,int(6/step):],i_grid[:,:int(6/step)],axis=1)
                s_grid = np.append(s_grid[:,int(6/step):],s_grid[:,:int(6/step)],axis=1)
                
            if date == '20200220':
                i_grid = np.append(i_grid[:,int(10/step):],i_grid[:,:int(10/step)],axis=1)
                s_grid = np.append(s_grid[:,int(10/step):],s_grid[:,:int(10/step)],axis=1)
                
            if date == '20200330':
                i_grid = np.append(i_grid[:,int(-510/step):],i_grid[:,:int(-510/step)],axis=1)
                s_grid = np.append(s_grid[:,int(-510/step):],s_grid[:,:int(-510/step)],axis=1)
                
            if date == '20200406':
                i_grid = np.append(i_grid[:,int(140/step):],i_grid[:,:int(140/step)],axis=1)
                s_grid = np.append(s_grid[:,int(140/step):],s_grid[:,:int(140/step)],axis=1)
                
            if date == '20200426':
                i_grid = np.append(i_grid[:,int(-484/step):],i_grid[:,:int(-484/step)],axis=1)
                s_grid = np.append(s_grid[:,int(-484/step):],s_grid[:,:int(-484/step)],axis=1)
                
            if date == '20200507':
                i_grid = np.append(i_grid[:,int(-467/step):],i_grid[:,:int(-467/step)],axis=1)
                s_grid = np.append(s_grid[:,int(-467/step):],s_grid[:,:int(-467/step)],axis=1)    
                        
            #move along x axis
            if date == '20191031' or date == '20191107' or date == '20191114':
                i_grid = np.append(i_grid[int(490/step):,:],i_grid[:int(490/step),:],axis=0)
                s_grid = np.append(s_grid[int(490/step):,:],s_grid[:int(490/step),:],axis=0)
                
            if date == '20191205':
                i_grid = np.append(i_grid[int(26/step):,:],i_grid[:int(26/step),:],axis=0)
                s_grid = np.append(s_grid[int(26/step):,:],s_grid[:int(26/step),:],axis=0)
                
            if date == '20200102':
                i_grid = np.append(i_grid[int(-14/step):,:],i_grid[:int(-14/step),:],axis=0)
                s_grid = np.append(s_grid[int(-14/step):,:],s_grid[:int(-14/step),:],axis=0)
                
            if date == '20200109':
                i_grid = np.append(i_grid[int(-4/step):,:],i_grid[:int(-4/step),:],axis=0)
                s_grid = np.append(s_grid[int(-4/step):,:],s_grid[:int(-4/step),:],axis=0)
                    
            if date == '20200227':
                i_grid = np.append(i_grid[int(8/step):,:],i_grid[:int(8/step),:],axis=0)
                s_grid = np.append(s_grid[int(8/step):,:],s_grid[:int(8/step),:],axis=0)
                
            if date == '20200130':
                i_grid = np.append(i_grid[int(10/step):,:],i_grid[:int(10/step),:],axis=0)
                s_grid = np.append(s_grid[int(10/step):,:],s_grid[:int(10/step),:],axis=0)   
                
            if date == '20200206':
                i_grid = np.append(i_grid[int(12/step):,:],i_grid[:int(12/step),:],axis=0)
                s_grid = np.append(s_grid[int(12/step):,:],s_grid[:int(12/step),:],axis=0)
            
            if date == '20200220':
                i_grid = np.append(i_grid[int(16/step):,:],i_grid[:int(16/step),:],axis=0)
                s_grid = np.append(s_grid[int(16/step):,:],s_grid[:int(16/step),:],axis=0)
                
            if date == '20200305'  or date == '20191226':
                i_grid = np.append(i_grid[int(14/step):,:],i_grid[:int(14/step),:],axis=0)
                s_grid = np.append(s_grid[int(14/step):,:],s_grid[:int(14/step),:],axis=0)   
                
            if date == '20200330':
                i_grid = np.append(i_grid[int(-280/step):,:],i_grid[:int(-280/step),:],axis=0)
                s_grid = np.append(s_grid[int(-280/step):,:],s_grid[:int(-280/step),:],axis=0)
            
            if date == '20200406': #for this case the axes are mixed up...
                i_grid = np.append(i_grid[int(-490/step):,:],i_grid[:int(-490/step),:],axis=0)
                s_grid = np.append(s_grid[int(-490/step):,:],s_grid[:int(-490/step),:],axis=0)
            
            if date == '20200426':
                i_grid = np.append(i_grid[int(-160/step):,:],i_grid[:int(-160/step),:],axis=0)
                s_grid = np.append(s_grid[int(-160/step):,:],s_grid[:int(-160/step),:],axis=0)
                
            if date == '20200507':
                i_grid = np.append(i_grid[int(-234/step):,:],i_grid[:int(-234/step),:],axis=0)
                s_grid = np.append(s_grid[int(-234/step):,:],s_grid[:int(-234/step),:],axis=0)
            
            #rotate
            #chose order=1 for no interpolation at boundaries!
            #chose mode='nearest' to have no boundary effect!
            if date == '20191031' or date == '20191107' or date == '20191114':
                i_grid = ndimage.rotate(i_grid, -3.5, reshape=False,order=0,mode='nearest')   #rotate by x degree
                s_grid = ndimage.rotate(s_grid, -3.5, reshape=False,order=0,mode='nearest')
                
            if date=='20200102' or date == '20200220':
                i_grid = ndimage.rotate(i_grid, -1, reshape=False,order=0,mode='nearest')
                s_grid = ndimage.rotate(s_grid, -1, reshape=False,order=0,mode='nearest')
                
            if date == '20200330':
                i_grid = ndimage.rotate(i_grid, 5, reshape=False,order=0,mode='nearest')
                s_grid = ndimage.rotate(s_grid, 5, reshape=False,order=0,mode='nearest')
                
            if date == '20200406':
                i_grid = ndimage.rotate(i_grid, 107, reshape=False,order=0,mode='nearest')
                s_grid = ndimage.rotate(s_grid, 107, reshape=False,order=0,mode='nearest')
            
            if date == '20200426':
                i_grid = ndimage.rotate(i_grid, 3, reshape=False,order=0,mode='nearest')
                s_grid = ndimage.rotate(s_grid, 3, reshape=False,order=0,mode='nearest')
                
            if date == '20200507':
                i_grid = ndimage.rotate(i_grid, 4, reshape=False,order=0,mode='nearest')
                s_grid = ndimage.rotate(s_grid, 4, reshape=False,order=0,mode='nearest')
            
            #check how it looks like after the lateral shifts
            tmpi = np.ma.array(i_grid,mask=i_grid<0).filled(np.nan)
            if dd == 0:
                i_grid2 = np.ma.masked_invalid(tmpi).filled(0)
            else:
                i_grid2 = i_grid2+np.ma.masked_invalid(tmpi).filled(0)
            del tmpi
            
            #slice and move for deformation (x-axis)
            if date == '20191031' or date == '20191107' or date == '20191114':
                #Large ridge in the corner (Stakes 2)
                i_grid[int(205/step):int(325/step),int(1630/step):int(1800/step)] = i_grid[int(150/step):int(270/step),int(1630/step):int(1800/step)]
                i_grid[int(170/step):int(230/step),int(1630/step):int(1800/step)] = np.nan
                
                s_grid[int(205/step):int(325/step),int(1630/step):int(1800/step)] = s_grid[int(150/step):int(270/step),int(1630/step):int(1800/step)]
                s_grid[int(170/step):int(230/step),int(1630/step):int(1800/step)] = np.nan
                
                #Rubble field after the ridge
                tmp = i_grid[int(120/step):int(170/step),int(1500/step):int(1650/step)]
                tmp = ndimage.rotate(tmp, 15, reshape=False,order=0,mode='nearest')
                i_grid[int(210/step):int(260/step),int(1520/step):int(1670/step)] = tmp
                i_grid[int(120/step):int(220/step),int(1500/step):int(1650/step)] = np.nan
                
                tmp = s_grid[int(120/step):int(170/step),int(1500/step):int(1650/step)]
                tmp = ndimage.rotate(tmp, 15, reshape=False,order=0,mode='nearest')
                s_grid[int(210/step):int(260/step),int(1520/step):int(1670/step)] = tmp
                s_grid[int(120/step):int(220/step),int(1500/step):int(1650/step)] = np.nan
                
                #End/Start (misterious lead) part
                tmp = i_grid[int(220/step):int(600/step),int(1340/step):int(1520/step)]
                tmp = ndimage.rotate(tmp, 7, reshape=False,order=0,mode='nearest')
                i_grid[int(250/step):int(630/step),int(1370/step):int(1550/step)] = tmp
                
                tmp = s_grid[int(220/step):int(600/step),int(1340/step):int(1520/step)]
                tmp = ndimage.rotate(tmp, 7, reshape=False,order=0,mode='nearest')
                s_grid[int(250/step):int(630/step),int(1370/step):int(1550/step)] = tmp
             
            if date == '20200406':
                i_grid[int(195/step):int(795/step),int(1350/step):int(1850/step)] = i_grid[int(200/step):int(800/step),int(1250/step):int(1750/step)]
                
                s_grid[int(195/step):int(795/step),int(1350/step):int(1850/step)] = s_grid[int(200/step):int(800/step),int(1250/step):int(1750/step)]
            
            if date == '20200426':
                #top
                i_grid[int(385/step):int(755/step),int(1680/step):int(1800/step)] = i_grid[int(380/step):int(750/step),int(1690/step):int(1810/step)]
                s_grid[int(385/step):int(755/step),int(1680/step):int(1800/step)] = s_grid[int(380/step):int(750/step),int(1690/step):int(1810/step)]
                
                #bottom
                i_grid[int(220/step):int(600/step),int(1380/step):int(1665/step)] = i_grid[int(220/step):int(600/step),int(1365/step):int(1650/step)]
                i_grid[int(400/step):int(600/step),int(1390/step):int(1510/step)] = i_grid[int(400/step):int(600/step),int(1380/step):int(1500/step)]
                
                s_grid[int(220/step):int(600/step),int(1380/step):int(1665/step)] = s_grid[int(220/step):int(600/step),int(1365/step):int(1650/step)]
                s_grid[int(400/step):int(600/step),int(1390/step):int(1510/step)] = s_grid[int(400/step):int(600/step),int(1380/step):int(1500/step)]
                                        
        if locs[ll]=='Nloop':
            #move along y axis
            if date == '20191024' or date == '20191031' or date == '20191107' :
                i_grid = np.append(i_grid[:,int(6/step):],i_grid[:,:int(6/step)],axis=1)            #this is same as numpy.roll
                s_grid = np.append(s_grid[:,int(6/step):],s_grid[:,:int(6/step)],axis=1)
            
            if date == '20191114':
                i_grid = np.append(i_grid[:,int(12/step):],i_grid[:,:int(12/step)],axis=1)
                s_grid = np.append(s_grid[:,int(12/step):],s_grid[:,:int(12/step)],axis=1)
                
            if date == '20191128' or date=='20200227':
                i_grid = np.append(i_grid[:,int(-2/step):],i_grid[:,:int(-2/step)],axis=1)
                s_grid = np.append(s_grid[:,int(-2/step):],s_grid[:,:int(-2/step)],axis=1) 
             
            if date == '20191205' or date == '20191219' or date == '20191226':
                i_grid = np.append(i_grid[:,int(-12/step):],i_grid[:,:int(-12/step)],axis=1)
                s_grid = np.append(s_grid[:,int(-12/step):],s_grid[:,:int(-12/step)],axis=1)
                
            if date == '20200102':
                i_grid = np.append(i_grid[:,int(12/step):],i_grid[:,:int(12/step)],axis=1)
                s_grid = np.append(s_grid[:,int(12/step):],s_grid[:,:int(12/step)],axis=1)
                
            if date=='20200227' or date == '20200305':
                i_grid = np.append(i_grid[:,int(-4/step):],i_grid[:,:int(-4/step)],axis=1)
                s_grid = np.append(s_grid[:,int(-4/step):],s_grid[:,:int(-4/step)],axis=1)    
                
            if date == '20200320':
                i_grid = np.append(i_grid[:,int(-10/step):],i_grid[:,:int(-10/step)],axis=1)
                s_grid = np.append(s_grid[:,int(-10/step):],s_grid[:,:int(-10/step)],axis=1)  
                
            if date == '20200326':
                i_grid = np.append(i_grid[:,int(40/step):],i_grid[:,:int(40/step)],axis=1)
                s_grid = np.append(s_grid[:,int(40/step):],s_grid[:,:int(40/step)],axis=1)
                
            if date == '20200403':
                i_grid = np.append(i_grid[:,int(1000/step):],i_grid[:,:int(1000/step)],axis=1)
                s_grid = np.append(s_grid[:,int(1000/step):],s_grid[:,:int(1000/step)],axis=1)    
            
            if date == '20200416':
                i_grid = np.append(i_grid[:,int(35/step):],i_grid[:,:int(35/step)],axis=1)
                s_grid = np.append(s_grid[:,int(35/step):],s_grid[:,:int(35/step)],axis=1)
                
            if date == '20200424' or date =='20200430' or date == '20200507':
                i_grid = np.append(i_grid[:,int(30/step):],i_grid[:,:int(30/step)],axis=1)
                s_grid = np.append(s_grid[:,int(30/step):],s_grid[:,:int(30/step)],axis=1)
                
            
            #move along x axis
            if date == '20191114' or date == '20191121' or date == '20191128' or date=='20200206':
                i_grid = np.append(i_grid[int(4/step):,:],i_grid[:int(4/step),:],axis=0)
                s_grid = np.append(s_grid[int(4/step):,:],s_grid[:int(4/step),:],axis=0)
                
            if date == '20200102':
                i_grid = np.append(i_grid[int(-4/step):,:],i_grid[:int(-4/step),:],axis=0)
                s_grid = np.append(s_grid[int(-4/step):,:],s_grid[:int(-4/step),:],axis=0)
                
            if date=='20200227' or date == '20200305':
                i_grid = np.append(i_grid[int(2/step):,:],i_grid[:int(2/step),:],axis=0)
                s_grid = np.append(s_grid[int(2/step):,:],s_grid[:int(2/step),:],axis=0)
                
            if date == '20200320':
                i_grid = np.append(i_grid[int(14/step):,:],i_grid[:int(14/step),:],axis=0)
                s_grid = np.append(s_grid[int(14/step):,:],s_grid[:int(14/step),:],axis=0)
                
            if date == '20200326':
                i_grid = np.append(i_grid[int(4/step):,:],i_grid[:int(4/step),:],axis=0)
                s_grid = np.append(s_grid[int(4/step):,:],s_grid[:int(4/step),:],axis=0)
                
            if date == '20200416'  or date == '20200424':
                i_grid = np.append(i_grid[int(26/step):,:],i_grid[:int(26/step),:],axis=0)
                s_grid = np.append(s_grid[int(26/step):,:],s_grid[:int(26/step),:],axis=0) 
                
            if date =='20200430' or date == '20200507':
                i_grid = np.append(i_grid[int(8/step):,:],i_grid[:int(8/step),:],axis=0)
                s_grid = np.append(s_grid[int(8/step):,:],s_grid[:int(8/step),:],axis=0)  
                
            #rotate
            #chose order=1 for no interpolation at boundaries!
            #chose mode='nearest' to have no boundary effect!
            if date=='20200102':
                i_grid = ndimage.rotate(i_grid, -1, reshape=False,order=0,mode='nearest')
                s_grid = ndimage.rotate(s_grid, -1, reshape=False,order=0,mode='nearest')
                
            if date == '20200320':
                i_grid = ndimage.rotate(i_grid, 2, reshape=False,order=0,mode='nearest')
                s_grid = ndimage.rotate(s_grid, 2, reshape=False,order=0,mode='nearest')
                
            if date == '20200326':
                i_grid = ndimage.rotate(i_grid, 8, reshape=False,order=0,mode='nearest')
                s_grid = ndimage.rotate(s_grid, 8, reshape=False,order=0,mode='nearest')
                
            if date == '20200403':
                i_grid = ndimage.rotate(i_grid, 111, reshape=False,order=0,mode='nearest')
                s_grid = ndimage.rotate(s_grid, 111, reshape=False,order=0,mode='nearest')
                
            if date == '20200416':
                i_grid = ndimage.rotate(i_grid, 7, reshape=False,order=0,mode='nearest')
                s_grid = ndimage.rotate(s_grid, 7, reshape=False,order=0,mode='nearest')
            
            if date == '20200424':
                i_grid = ndimage.rotate(i_grid, 6, reshape=False,order=0,mode='nearest')
                s_grid = ndimage.rotate(s_grid, 6, reshape=False,order=0,mode='nearest')
            
            if date =='20200430'  or date == '20200507':
                i_grid = ndimage.rotate(i_grid, 5, reshape=False,order=0,mode='nearest')
                s_grid = ndimage.rotate(s_grid, 5, reshape=False,order=0,mode='nearest')
                
            
            #this one it too far away
            if date == '20200403':
                i_grid[int(1350/step):int(1765/step),int(650/step):int(1150/step)] = i_grid[int(285/step):int(700/step),int(100/step):int(600/step)]
                i_grid[int(285/step):int(700/step),int(100/step):int(600/step)] = np.nan
                
                s_grid[int(1350/step):int(1765/step),int(650/step):int(1150/step)] = s_grid[int(285/step):int(700/step),int(100/step):int(600/step)]
                s_grid[int(285/step):int(700/step),int(100/step):int(600/step)] = np.nan

            tmpi = np.ma.array(i_grid,mask=i_grid<0).filled(np.nan)
            if dd == 0:
                i_grid2 = np.ma.masked_invalid(tmpi).filled(0)
            else:
                i_grid2 = i_grid2+np.ma.masked_invalid(tmpi).filled(0)
            del tmpi
             
            #slice and move for deformation (x-axis)
            if date == '20200320':
                #Lunch Lead
                i_grid[int(1080/step):int(1680/step),int(20/step):int(820/step)] = i_grid[int(1100/step):int(1700/step),int(0/step):int(800/step)]
                i_grid[int(1080/step):int(1480/step),int(1000/step):int(1200/step)] = i_grid[int(1080/step):int(1480/step),int(1050/step):int(1250/step)]
                
                s_grid[int(1080/step):int(1680/step),int(20/step):int(820/step)] = s_grid[int(1100/step):int(1700/step),int(0/step):int(800/step)]
                s_grid[int(1080/step):int(1480/step),int(1000/step):int(1200/step)] = s_grid[int(1080/step):int(1480/step),int(1050/step):int(1250/step)]
                
            if date == '20200326':
                #Lunch Lead head
                i_grid[int(1335/step):int(1485/step),int(650/step):int(845/step)] = i_grid[int(1350/step):int(1500/step),int(650/step):int(845/step)]
                i_grid[int(1370/step):int(1400/step),int(730/step):int(780/step)] = i_grid[int(1365/step):int(1395/step),int(655/step):int(705/step)]
                i_grid[int(1355/step):int(1410/step),int(650/step):int(730/step)] = np.nan
                
                #Lunch Lead leg
                i_grid[int(1310/step):int(1510/step),int(920/step):int(1120/step)] = i_grid[int(1300/step):int(1500/step),int(950/step):int(1150/step)]
                i_grid[int(1310/step):int(1510/step),int(1120/step):int(1150/step)] = np.nan
                
               #Lunch Lead head
                s_grid[int(1335/step):int(1485/step),int(650/step):int(845/step)] = s_grid[int(1350/step):int(1500/step),int(650/step):int(845/step)]
                s_grid[int(1370/step):int(1400/step),int(730/step):int(780/step)] = s_grid[int(1365/step):int(1395/step),int(655/step):int(705/step)]
                s_grid[int(1355/step):int(1410/step),int(650/step):int(730/step)] = np.nan
                
                #Lunch Lead leg
                s_grid[int(1310/step):int(1510/step),int(920/step):int(1120/step)] = s_grid[int(1300/step):int(1500/step),int(950/step):int(1150/step)]
                s_grid[int(1310/step):int(1510/step),int(1120/step):int(1150/step)] = np.nan
                
            if date == '20200403':               
                #head
                i_grid[int(1350/step):int(1450/step),int(750/step):int(790/step)] = i_grid[int(1350/step):int(1450/step),int(720/step):int(760/step)]
                i_grid[int(1350/step):int(1450/step),int(720/step):int(750/step)] = np.nan
                
                s_grid[int(1350/step):int(1450/step),int(750/step):int(790/step)] = s_grid[int(1350/step):int(1450/step),int(720/step):int(760/step)]
                s_grid[int(1350/step):int(1450/step),int(720/step):int(750/step)] = np.nan
                
                #leg
                i_grid[int(1350/step):int(1505/step),int(875/step):int(1125/step)] = i_grid[int(1340/step):int(1495/step),int(900/step):int(1150/step)]
                s_grid[int(1350/step):int(1505/step),int(875/step):int(1125/step)] = s_grid[int(1340/step):int(1495/step),int(900/step):int(1150/step)]
            
            if date == '20200416':               
                #Lunch Lead head
                i_grid[int(1340/step):int(1490/step),int(650/step):int(845/step)] = i_grid[int(1350/step):int(1500/step),int(650/step):int(845/step)]
                i_grid[int(1360/step):int(1430/step),int(750/step):int(790/step)] = i_grid[int(1360/step):int(1430/step),int(730/step):int(770/step)]
                i_grid[int(1350/step):int(1430/step),int(730/step):int(750/step)] = np.nan
                
                s_grid[int(1340/step):int(1490/step),int(650/step):int(845/step)] = s_grid[int(1350/step):int(1500/step),int(650/step):int(845/step)]
                s_grid[int(1360/step):int(1430/step),int(750/step):int(790/step)] = s_grid[int(1360/step):int(1430/step),int(730/step):int(770/step)]
                s_grid[int(1350/step):int(1430/step),int(730/step):int(750/step)] = np.nan
                
                #Lunch Lead leg
                i_grid[int(1325/step):int(1480/step),int(870/step):int(1120/step)] = i_grid[int(1305/step):int(1460/step),int(900/step):int(1150/step)]
                i_grid[int(1310/step):int(1510/step),int(1120/step):int(1150/step)] = np.nan
                
                s_grid[int(1325/step):int(1480/step),int(870/step):int(1120/step)] = s_grid[int(1305/step):int(1460/step),int(900/step):int(1150/step)]
                s_grid[int(1310/step):int(1510/step),int(1120/step):int(1150/step)] = np.nan

            if date == '20200424':               
                #Lunch Lead head
                i_grid[int(1340/step):int(1490/step),int(650/step):int(845/step)] = i_grid[int(1350/step):int(1500/step),int(650/step):int(845/step)]
                i_grid[int(1360/step):int(1430/step),int(750/step):int(790/step)] = i_grid[int(1360/step):int(1430/step),int(730/step):int(770/step)]
                i_grid[int(1350/step):int(1430/step),int(730/step):int(750/step)] = np.nan
                
                s_grid[int(1340/step):int(1490/step),int(650/step):int(845/step)] = s_grid[int(1350/step):int(1500/step),int(650/step):int(845/step)]
                s_grid[int(1360/step):int(1430/step),int(750/step):int(790/step)] = s_grid[int(1360/step):int(1430/step),int(730/step):int(770/step)]
                s_grid[int(1350/step):int(1430/step),int(730/step):int(750/step)] = np.nan
                
                #leg
                sample = i_grid[int(1300/step):int(1455/step),int(860/step):int(1125/step)]
                rsample = ndimage.rotate(sample, -5, reshape=False,order=0,mode='nearest')
                i_grid[int(1325/step):int(1480/step),int(855/step):int(1120/step)] = rsample
                
                sample = s_grid[int(1300/step):int(1455/step),int(860/step):int(1125/step)]
                rsample = ndimage.rotate(sample, -5, reshape=False,order=0,mode='nearest')
                s_grid[int(1325/step):int(1480/step),int(855/step):int(1120/step)] = rsample
                
            if date =='20200430'  or date == '20200507':                               
                #Lunch Lead head
                i_grid[int(1340/step):int(1490/step),int(650/step):int(845/step)] = i_grid[int(1350/step):int(1500/step),int(650/step):int(845/step)]
                i_grid[int(1360/step):int(1430/step),int(750/step):int(790/step)] = i_grid[int(1360/step):int(1430/step),int(730/step):int(770/step)]
                i_grid[int(1350/step):int(1430/step),int(730/step):int(750/step)] = np.nan
                
                s_grid[int(1340/step):int(1490/step),int(650/step):int(845/step)] = s_grid[int(1350/step):int(1500/step),int(650/step):int(845/step)]
                s_grid[int(1360/step):int(1430/step),int(750/step):int(790/step)] = s_grid[int(1360/step):int(1430/step),int(730/step):int(770/step)]
                s_grid[int(1350/step):int(1430/step),int(730/step):int(750/step)] = np.nan

                #leg
                sample = i_grid[int(1300/step):int(1455/step),int(860/step):int(1125/step)]
                rsample = ndimage.rotate(sample, -5, reshape=False,order=0,mode='nearest')
                i_grid[int(1310/step):int(1465/step),int(855/step):int(1120/step)] = rsample
                
                sample = s_grid[int(1300/step):int(1455/step),int(860/step):int(1125/step)]
                rsample = ndimage.rotate(sample, -5, reshape=False,order=0,mode='nearest')
                s_grid[int(1310/step):int(1465/step),int(855/step):int(1120/step)] = rsample
                
        if locs[ll]=='snow1':
            #move along y axis
            if date == '20191222':
                i_grid = np.append(i_grid[:,int(-2/step):],i_grid[:,:int(-2/step)],axis=1)
                s_grid = np.append(s_grid[:,int(-2/step):],s_grid[:,:int(-2/step)],axis=1)
                
            if date == '20200112':
                i_grid = np.append(i_grid[:,int(-8/step):],i_grid[:,:int(-8/step)],axis=1)
                s_grid = np.append(s_grid[:,int(-8/step):],s_grid[:,:int(-8/step)],axis=1)    
                
            if date == '20200126':
                i_grid = np.append(i_grid[:,int(-2/step):],i_grid[:,:int(-2/step)],axis=1)
                s_grid = np.append(s_grid[:,int(-2/step):],s_grid[:,:int(-2/step)],axis=1)
                            
            if date == '20200406':
                i_grid = np.append(i_grid[:,int(177/step):],i_grid[:,:int(177/step)],axis=1)
                s_grid = np.append(s_grid[:,int(177/step):],s_grid[:,:int(177/step)],axis=1)

            #move along x axis
            if date == '20191222':
                i_grid = np.append(i_grid[int(12/step):,:],i_grid[:int(12/step),:],axis=0)
                s_grid = np.append(s_grid[int(12/step):,:],s_grid[:int(12/step),:],axis=0)
                
            if date == '20200112':
                i_grid = np.append(i_grid[int(-18/step):,:],i_grid[:int(-18/step),:],axis=0)
                s_grid = np.append(s_grid[int(-18/step):,:],s_grid[:int(-18/step),:],axis=0)
            
            if date == '20200126':
                i_grid = np.append(i_grid[int(1/step):,:],i_grid[:int(1/step),:],axis=0)
                s_grid = np.append(s_grid[int(1/step):,:],s_grid[:int(1/step),:],axis=0)
                            
            if date == '20200406': #for this case the axes are mixed up...
                i_grid = np.append(i_grid[int(-586/step):,:],i_grid[:int(-586/step),:],axis=0)
                s_grid = np.append(s_grid[int(-586/step):,:],s_grid[:int(-586/step),:],axis=0)

            #rotate
            if date == '20200406':
                i_grid = ndimage.rotate(i_grid, 107, reshape=False,order=0,mode='nearest')
                s_grid = ndimage.rotate(s_grid, 107, reshape=False,order=0,mode='nearest')
                
            #check how it looks like after the lateral shifts
            tmpi = np.ma.array(i_grid,mask=i_grid<0).filled(np.nan)
            if dd == 0:
                i_grid2 = np.ma.masked_invalid(tmpi).filled(0)
            else:
                i_grid2 = i_grid2+np.ma.masked_invalid(tmpi).filled(0)
            del tmpi

        #if locs[ll]=='transect':
                        
            ##rotate
            #if date == '20200630':
                #i_grid = ndimage.rotate(i_grid, -40, reshape=False,order=0,mode='nearest')
                #s_grid = ndimage.rotate(s_grid, -40, reshape=False,order=0,mode='nearest')
                
            ##move along x axis
            #if date == '20200630':
                #i_grid = np.append(i_grid[int(-1320/step):,:],i_grid[:int(-1320/step),:],axis=0)
                #s_grid = np.append(s_grid[int(-1320/step):,:],s_grid[:int(-1320/step),:],axis=0)
            
            
        
        i_grid = np.ma.array(i_grid,mask=i_grid<0).filled(np.nan)
        s_grid = np.ma.array(s_grid,mask=s_grid<0).filled(np.nan)
        
        #lets check how this looks like after the adjusting
        if dd == 0:
            i_grid3 = np.ma.masked_invalid(i_grid).filled(0)
        else:
            i_grid3 = i_grid3+np.ma.masked_invalid(i_grid).filled(0)
        
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
    
    #uniform values
    i_grid1 = np.where(i_grid1>0,1,i_grid1)
    i_grid2 = np.where(i_grid2>0,1,i_grid2)
    i_grid3 = np.where(i_grid3>0,1,i_grid3)
    
    #plot
    ax.imshow(i_grid1.T, extent=extent, origin='lower',vmin=0,vmax=6,cmap=plt.cm.rainbow)   #make it purple
    bx.imshow(i_grid2.T, extent=extent, origin='lower',vmin=0,vmax=6,cmap=plt.cm.rainbow)
    cx.imshow(i_grid3.T, extent=extent, origin='lower',vmin=0,vmax=6,cmap=plt.cm.rainbow)
    
    #get plots with coordinates
    if locs[ll]=='transect':
        x_grid = ndimage.rotate(x_grid, 40, reshape=False,order=0,mode='nearest')
        y_grid = ndimage.rotate(y_grid, 40, reshape=False,order=0,mode='nearest')
        
        x_grid = x_grid+1320
        y_grid = y_grid+10
        
        dx.contourf(x_grid.T, y_grid.T, i_grid3.T)
    
    if locs[ll]=='special':
        x_grid = ndimage.rotate(x_grid, 40, reshape=False,order=0,mode='nearest')
        y_grid = ndimage.rotate(y_grid, 40, reshape=False,order=0,mode='nearest')
        
        x_grid = x_grid+1200
        y_grid = y_grid+150
        
        dx.contourf(x_grid.T, y_grid.T, i_grid3.T)
        
    else:
        dx.contourf(x_grid.T, y_grid.T, i_grid3.T)
    
    del x_grid, y_grid, s_grid, i_grid
    del i_grid1, i_grid2, i_grid3
    
#plt.show()    
fig1.savefig(outpath+outname,bbox_inches='tight')
#fig2.savefig(outpath+outname2,bbox_inches='tight')
