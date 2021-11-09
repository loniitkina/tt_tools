import numpy as np
from glob import glob
from tt_func import getColumn, running_stats
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


#location and dates
locs = ['Sloop']#,
#locs = ['Nloop']


colors = plt.cm.rainbow(np.linspace(0, 1, len(locs)))
    

inpath_table = '../data/MCS/MP/'
inpath_grid = '../data/grids_AGU/'
inpath_weather = '../data/weather/'
outpath = '../plots_AGU/'
outpath = '../plots_gridded/'

step = 1
stp = str(step)
method_gem2 = 'nearest'
ch_name = '_18kHz'

#Rougness scatter plot
fig4 = plt.figure(figsize=(10,10))
ax = fig4.add_subplot(111)
#ax.set_title(title, fontsize=25)
ax.set_xlabel('Roughness (m)', fontsize=20)
ax.set_ylabel('Snow change (m)', fontsize=20)
ax.tick_params(axis="x", labelsize=14)
ax.tick_params(axis="y", labelsize=14)
#ax.set_xlim(0,1)
#ax.set_ylim(0,1)

x_list=[]
y_list=[]

for i in range(0,len(locs)):
    loc=locs[i]
    #get data
    inf = inpath_grid+loc+'_'+stp+'m_'+method_gem2+ch_name+'_track.npz'
    #inf = inpath_grid+loc+'_'+stp+'m_'+method_gem2+ch_name+'_track1.npz'
    data = np.load(inf)
    transect_snow = data['snow']
    transect_ice = data['ice']
    si = transect_snow[:,2:]    #first two columns are coordinates
    it = transect_ice[:,2:]
    si = np.ma.masked_invalid(si)
    it = np.ma.masked_invalid(it)
                    
    #time derivative of snow depth (erosion=negative!)
    #start with the last deformation: 5 December 2019
    if loc=='Sloop':
        ##whole season (before lead): 20191031 and 20200330 - this has no erosion, r2=0.5
        #dsi_s = si[:,-4]-si[:,0]
        #it = it[:,-4]

        ###or at last low roughness correlation: 20200102 and 20200227 - has some erosion, r2=0.34
        #dsi_s = si[:,-6]-si[:,5]
        #it = it[:,5]
        
        ##large dune formation and mean snow depth decrease end of February: snow moves on level ice
        dsi_s = si[:,11]-si[:,10]
        it = it[:,11]
        
        ###large dune formation and mean snow depth decrease end of February-March: snow eroded from the ridges
        #dsi_s = si[:,12]-si[:,11]
        #it = it[:,12]
        
        
    if loc=='Nloop':
        ##April minus 5 Dec
        #dsi_s = si[:,-2]-si[:,6]
        ##March minus 5 Dec
        #dsi_s = si[:,-6]-si[:,6]
        #it = it[:,6]
        
        ###or at last low roughness correlation: 27 February 2020
        #dsi_s = si[:,-6]-si[:,9]
        #it = it[:,9]
        
        ###large dune formation after strong snow drift event (Wagner)
        #dsi_s = si[:,14]-si[:,13]
        #it = it[:,14]
        
        ##large dune formation after strong snow drift event (Wagner)
        dsi_s = si[:,15]-si[:,14]
        it = it[:,14]

        
    #roughness
    nit=30
    itm,itv = running_stats(it,nit)
    std = np.sqrt(itv)

    #snow
    nit=30
    dsi_sm,tmp = running_stats(dsi_s,nit)
    
    #plotting
    ax.scatter(std,dsi_sm,alpha=0.3,c=colors[i])
    
    
    x_list.extend(std)
    y_list.extend(dsi_sm)

#linear regression model
x = np.ma.masked_invalid(x_list)
y = np.array(y_list)[x.mask == False]
x=x.compressed()
y = np.ma.masked_invalid(y)
x = x[y.mask == False]
y=y.compressed()
print(x.shape)
print(y.shape)

model = np.polyfit(x, y, 1)
print('coefficients: ', model)

predict = np.poly1d(model)
from sklearn.metrics import r2_score
r2 = r2_score(y, predict(x))
print('R2: ',r2)

x_lin_reg = np.arange(0, 1.1,.1)
y_lin_reg = predict(x_lin_reg)

ax.plot(x_lin_reg, y_lin_reg, c='k', label='season')


#plot shows how the running mean values are not independent, are not uniformly scattered, and align along some patterns.
#large oscillations in the ridges, huge accummulation, but also highest erosion. This is very dependent on the wind direction. This is only partially removed from analysis by running means.
#for Nloop there is no such clear relationship: very little level ice, lots of deformed ice along various directions
ax.legend()
fig4.savefig(outpath+'derivative2_'+loc,bbox_inches='tight')



#profile plot
mxx = transect_snow[:,0]
myy = transect_snow[:,1]

#get distances between fixed date MP points
dx = mxx[1:]-mxx[:-1]
dy = myy[1:]-myy[:-1]
md = np.sqrt(dx**2+dy**2)

#what is the surface elevation? ALS geotiff???
#hydrostatic equilibrium with mean snow density and sea ice density
rho_i = 882
rho_w = 1025
rho_s = 313

#plot
fig1 = plt.figure(figsize=(20,10))
#fig1 = plt.figure(figsize=(40,20))
fig1.patch.set_facecolor('0.5')
fig1.patch.set_facecolor('1')

ax = fig1.add_subplot(111)
ax.set_xlabel('Length (m)', fontsize=25)
#ax.set_title(title+datel[dd], fontsize=30)
ax.set_ylabel('Distance from water surface (m)', fontsize=25)
ax.tick_params(axis="x", labelsize=24)
ax.tick_params(axis="y", labelsize=24)
ax.set_facecolor('0.3')

#what is the surface elevation? ALS geotiff???
#hydrostatic equilibtium with mean snow density and sea ice density
rho_i = 882
rho_w = 1025
rho_s = 313

#following Forsstrom et al, 2011, Annals of Glaciology
#fb = (it - si[:,-4] * (rho_s/(rho_w-rho_i))) * (rho_w-rho_i)/rho_w
fb = (it - si[:,5] * (rho_s/(rho_w-rho_i))) * (rho_w-rho_i)/rho_w
    
#cumulative distance allong the fixed date MP transect
x = np.zeros_like(fb)
x[1:] = np.cumsum(md)

#plot with equilibrium
ax.plot(x,fb,label='ice surface',c='k',ls=':')
#ax.fill_between(x, fb, fb+si[:,0],alpha=.5, color='y', label='snow 2019/10/31')
#ax.fill_between(x, fb, fb+si[:,-4],alpha=.3, color='b', label='snow 2020/03/30')
#ax.fill_between(x, fb, fb-it,alpha=.6, color='0.5', label='ice 2020/03/30')

ax.fill_between(x, fb, fb+si[:,11],alpha=.5, color='y', label='snow 2020/02/20')
ax.fill_between(x, fb, fb+si[:,12],alpha=.3, color='b', label='snow 2020/02/27')
ax.fill_between(x, fb, fb-it,alpha=.6, color='0.5', label='ice 2020/02/27')


ax.legend(fontsize=25,loc='lower left',fancybox=True,facecolor=fig1.get_facecolor(),framealpha=.6)
fig1.savefig(outpath+'profile_diff_change'+loc,bbox_inches='tight', facecolor=fig1.get_facecolor(), edgecolor='none')


#volume fraction estimate
vol_frac_diff=(np.sum(si[:,14])-np.sum(si[:,15]))/np.sum(si[:,14])
print(vol_frac_diff)

