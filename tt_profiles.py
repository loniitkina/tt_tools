import numpy as np
from glob import glob
from tt_func import getColumn
import matplotlib.pyplot as plt

#grid parameters
stp = 5        #grid spacing in meters 
maxdist = stp   #how far away to search in case of nan
#maxdist = 5

##location and dates
#loc = 'Sloop'
#dates = ['20191107','20191205','20200227','20200330','20200426']
#datel = ['2019/11/07','2019/12/05','2020/02/27','2020/03/30','2020/04/26']
#title='Southeren transect loop '

loc = 'Nloop'
#dates = ['20191107','20191114','20191205','20191219','20200102','20200109','20200130','20200206','20200220','20200227','20200305','20200416','20200430'] #Nloop
dates = ['20191205','20191219','20200220','20200227','20200305']
datel = ['2019/12/05','2019/12/19','2020/02/20','2020/02/27','2020/03/05']
title='Northern transect loop '


print(loc)
#colors = plt.cm.rainbow(np.linspace(0, 1, len(dates)))
colors = plt.cm.Blues(np.linspace(0, 1, len(dates)))

inpath = '../data/MCS/MP/'
outpath = '../plots_AGU/'
inpath_grid = '../data/grids_AGU/'

fb_list=[]
si_list=[]
ii_list=[]
x_list=[]

for dd in range(0,len(dates)):
    date = dates[dd]
    print(date)
    
    outname = 'profile_'+date+'_'+loc+str(stp)+'.png'
    
    #choose one 'most perfct' MP track to compare to the others
    fixed_date=date
    fname = glob(inpath+'*/magnaprobe-transect-'+date+'*'+loc+'-track-icecs-xy_corr.csv')[0]
    print(fname)
    mxx = getColumn(fname,3, delimiter=',', magnaprobe=False)
    mxx = np.array(mxx,dtype=np.float)

    myy = getColumn(fname,4, delimiter=',', magnaprobe=False)
    myy = np.array(myy,dtype=np.float)

    #get distances between fixed date MP points
    dx = mxx[1:]-mxx[:-1]
    dy = myy[1:]-myy[:-1]
    md = np.sqrt(dx**2+dy**2)

    #what is the surface elevation? ALS geotiff???
    #hydrostatic equilibtium with mean snow density and sea ice density
    rho_i = 882
    rho_w = 1025
    rho_s = 313

    #plot
    fig1 = plt.figure(figsize=(20,10))
    fig1.patch.set_facecolor('0.5')
    
    ax = fig1.add_subplot(111)
    ax.set_xlabel('Length (m)', fontsize=20)
    ax.set_title(title+datel[dd], fontsize=25)
    ax.set_ylabel('Distance from water surface (m)', fontsize=20)
    ax.tick_params(axis="x", labelsize=14)
    ax.tick_params(axis="y", labelsize=14)

    
    ax.set_facecolor('0.3')
    
    
    #load all the gridded data
    of = inpath_grid+loc+'_'+date+'_'+str(stp)+'m.npz'
    #of = inpath_grid+loc+'_'+date+'_'+stp+'m_linear.npz')
    print(of)
    data = np.load(of)

    x_grid = data['x']
    y_grid = data['y']
    s_grid = data['snow']
    i_grid = data['ice']
    
    #quick check
    #ax.subplot(111)
    #ax.imshow(s_grid.T, extent=(-500,700,-900,700), origin='lower',vmin=0,vmax=1.2, cmap=cmaps[i])
    #ax.colorbar()
    #ax.title('Snow')
    #ax.gcf().set_size_inches(6, 6)
    #ax.show()
    #exit()

    #unroll the data back into the transect and draw them
    #find nearest grid point for each MP point of a sample MP transect (e.g. 20.2.2020)
    #order these grid points in a row

    si = []
    ii = []
    for i in range(0,len(mxx)):
        xi = mxx[i]
        yi = myy[i]
        #calculate all distances to grid points
        dg = np.sqrt((xi-x_grid)**2+(yi-y_grid)**2)
        #imin = np.min(dg)
        amin = np.argmin(dg)
        
        val_s = s_grid.flatten()[amin]
        val_i = i_grid.flatten()[amin]
        
        #if step < 5m, we need to take more distances to account, dont got further than maxdist away!
        if np.isnan(val_s):
            print('no value')
            dist = 0
            mask_dg = np.zeros_like(dg.flatten())
            while np.isnan(val_s) and dist < maxdist:
                mask_dg[amin]=1
                dg = np.ma.array(dg.flatten(),mask=mask_dg)
                amin = np.argmin(dg)
                dist = dg[amin]
                val_s = s_grid.flatten()[amin]
                val_i = i_grid.flatten()[amin]
            print(dist,val_s)
        
        si.append(val_s)
        ii.append(val_i)

    si = np.array(si)
    ii = np.array(ii)
    
    if loc=='Sloop' and date == '20191226':
        bad = np.zeros_like(ii)
        bad[700:] = 1
        ii = np.ma.array(ii,mask=bad)

    #what is the surface elevation? ALS geotiff???
    #hydrostatic equilibtium with mean snow density and sea ice density
    rho_i = 882
    rho_w = 1025
    rho_s = 313

    #following Forsstrom et al, 2011, Annals of Glaciology
    fb = (ii - si * (rho_s/(rho_w-rho_i))) * (rho_w-rho_i)/rho_w
    x = range(0,len(fb))
    
    #cumulative distance allong the fixed date MP transect
    x = np.zeros_like(fb)
    x[1:] = np.cumsum(md)
    #print(x)
    #exit()


    #it looks like they started somewhere else the last two times, still went same direction...
    if date=='20200330' or date=='20200426':
        fb = np.concatenate((fb[-215:],fb[:-215]))
        ii = np.concatenate((ii[-215:],ii[:-215]))
        si = np.concatenate((si[-215:],si[:-215]))
        
    #plot with equilibrium
    ax.plot(x,fb,label='ice surface',c='k',ls=':')
    
    #ax.plot(fb-ii,label='ice bottom'+date)
    #ax.plot(fb+si,label='snow surface'+date)
    ax.fill_between(x, fb, fb-ii,alpha=.6, color=colors[1], label='ice')
    ax.fill_between(x, fb, fb+si,alpha=.6, color=colors[0], label='snow')

    ax.set_ylim(-3.5,1.2)
    ax.set_xlim(0,x[-2])        #beacause last MP value/coordinate is typically same as first (at large distance)
    ax.legend(fontsize=20,loc='lower left',fancybox=True,facecolor=colors[0],framealpha=.6)
    print(outname)
    fig1.savefig(outpath+outname,bbox_inches='tight', facecolor=fig1.get_facecolor(), edgecolor='none')

    #save all these data and try to overlay them in a multi-profile plot
    from scipy.signal import savgol_filter
    fb_hat = savgol_filter(fb, 21, 3) # window size 51, polynomial order 3
    ii_hat = savgol_filter(ii, 21, 3)
    si_hat = savgol_filter(si, 21, 3)  
    
    fb_list.append(fb_hat)
    ii_list.append(ii_hat) 
    si_list.append(si_hat)
    x_list.append(x)
    
fig2 = plt.figure(figsize=(20,10))
ax = fig2.add_subplot(111)
ax.set_xlabel('Length (m)', fontsize=20)
ax.set_title(title+datel[-1], fontsize=25)
ax.set_ylabel('Distance from water surface (m)', fontsize=20)
ax.tick_params(axis="x", labelsize=14)
ax.tick_params(axis="y", labelsize=14)

for i in range(0,len(fb_list)):
    x=x_list[i]
    
    #ax.plot(x, fb_list[i],c='0.75')
    ax.plot(x, fb_list[i]-ii_list[i],c=colors[i],label=datel[i]+' bottom')
    #ax.plot(x, fb_list[i]+si_list[i],c='orange')

x=x_list[-1]
ax.plot(x,fb_list[-1],label='ice surface',c=colors[-1],ls=':')    
ax.fill_between(x, fb_list[-1], fb_list[-1]-ii_list[-1],alpha=.3, color=colors[-1], label='ice')
ax.fill_between(x, fb_list[-1], fb_list[-1]+si_list[-1],alpha=.3, color=colors[-2], label='snow')
    
#x=x_list[0]
#ax.plot(x,fb_list[0],label='ice surface',c='k')    

if loc=='Sloop':
    ax.set_xlim(0,1500)
if loc=='Nloop':
    ax.set_xlim(0,1200)

ax.legend(fontsize=20,loc='lower left',fancybox=True,facecolor=colors[-1],framealpha=.1)
outname = 'profile_all_'+loc+str(stp)+'.png'
fig2.savefig(outpath+outname,bbox_inches='tight')

#just snow
fig3 = plt.figure(figsize=(20,5))
ax = fig3.add_subplot(111)
ax.set_xlabel('Length (m)', fontsize=20)
ax.set_title(title+datel[-1], fontsize=25)
ax.set_ylabel('Distance from water surface (m)', fontsize=20)
ax.tick_params(axis="x", labelsize=14)
ax.tick_params(axis="y", labelsize=14)

for i in range(0,len(fb_list)-1):
    x=x_list[i]
    zero_level = np.zeros_like(x)
    
    #ax.plot(x, fb_list[i],c='0.75')
    ax.plot(x, zero_level+si_list[i],c=colors[i],label=datel[i]+' surface')

x=x_list[-1]
zero_level = np.zeros_like(x)
#ax.fill_between(x, fb_list[-1], fb_list[-1]-ii_list[-1],alpha=.3, color=colors[-1], label='ice')
ax.fill_between(x, zero_level, zero_level+si_list[-1],alpha=.3, color=colors[-2], label='snow')
    
#x=x_list[0]
#ax.plot(x,fb_list[0],label='ice surface',c='k')    
ax.set_ylim(0,1)
if loc=='Sloop':
    ax.set_xlim(0,1500)
if loc=='Nloop':
    ax.set_xlim(0,1300)
ax.legend(fontsize=20,loc='upper right',fancybox=True,facecolor=colors[-1],framealpha=.1)
outname = 'profile_snow_'+loc+str(stp)+'.png'
fig3.savefig(outpath+outname,bbox_inches='tight')

