import numpy as np
from glob import glob
from tt_func import getColumn
import matplotlib.pyplot as plt

##grid parameters
#stp = '5m'
#stp = '2m_linear'
#stp = '2m_nearest'
#maxdist = 10   #how far away to search in case of nan
##maxdist = 5

#window size for savgol smoothing savgol_filter (must be odd and more than polyorder=3)
polyorder=3
widow=21
window=5
#for point measurements (like ridges)
polyorder=0
window=1

#location and dates
#loc = 'Sloop'
#dates = ['20191107','20191205', '20200130' ,'20200227','20200305','20200426']
#datel = ['2019/11/07','2019/12/05','2020/01/30','2020/02/27','2020/03/05','2020/04/26']
#title='Southeren transect loop '

#loc = 'Nloop'
#dates = ['20191205','20191219','20200220','20200227','20200305','20200416','20200507']
#datel = ['2019/12/05','2019/12/19','2020/02/20','2020/02/27','2020/03/05','2020/04/16','2020/05/07']
#title='Northern transect loop '

#loc= 'snow1'
#dates = ['20191222','20200112','20200126','20200207']    #20200126 is reduced track (square!)
#datel = ['2019/12/22','2020/01/12','2020/01/26','2020/02/07']
#title='Snow1 transect '

#loc= 'special'
#dates = ['20200123']
#datel = ['2020/01/23']
#title='Long transect '

loc = 'ridgeFR1'
dates = ['20200108','20200119','20200221','20200305']
datel = ['2020/01/08','2020/01/19','2020/02/21','2020/03/05']
title = 'Fort Ridge Installation Transect '

#loc = 'ridgeFR2'    #coring
#dates = ['20200110','20200212','20200221']
#datel = ['2020/01/10','2020/02/12','2020/02/21']
#title = 'Fort Ridge Coring Transect '

loc = 'ridgeFR3'
dates = ['20200131']
datel = ['2020/01/31'] 
title = 'Fort Ridge Optics Transect '

#loc = 'ridgeA1'    #central
#dates = ['20200117','20200131','20200228']
#datel = ['2020/01/17','2020/01/31','2020/02/28']
#title = "Allie's Ridge Central Transect "

loc = 'ridgeA2'    #north
dates = ['20200212','20200228']
datel = ['2020/02/12','2020/02/28']
title = "Allie's Ridge North Transect "

loc = 'ridgeA3'    #south
dates = ['20200212','20200228']
datel = ['2020/02/12','2020/02/28']
title = "Allie's Ridge South Transect "


##comparable loop transects
#loc = 'Sloop'
#dates = ['20200130']
#datel = ['2020/01/30']
#title='Southeren transect loop '

#loc = 'runway'
#dates = ['20200207']
#datel = ['2020/02/07']
#title='Runway transect '

#dates = ['20200107']
#datel = ['2020/01/07']
#title='Dark Side FYI '

#dates = ['20200115']
#datel = ['2020/01/15']
#title='Dark Side SYI '


print(loc)
#colors = plt.cm.rainbow(np.linspace(0, 1, len(dates)))
colors = plt.cm.Blues(np.linspace(0, 1, len(dates)))

if len(dates) == 1:
    colors = ['.1','.5']
    

inpath_table = '../data/MCS/MP/'
outpath = '../plots_AGU/'
#inpath_grid = '../data/grids_AGU/'

fb_list=[]
si_list=[]
ii_list=[]
x_list=[]

for dd in range(0,len(dates)):
    date = dates[dd]
    print(date)
    
    outname = 'profile_'+date+'_'+loc+'gridded.png'
    
    #choose one 'most perfct' MP track to compare to the others
    fname = glob(inpath_table+'*/magna+gem2-transect-'+date+'*'+loc+'.csv')[0]
    print(fname)
    mxx = getColumn(fname,3, delimiter=',', magnaprobe=False)
    myy = getColumn(fname,4, delimiter=',', magnaprobe=False)
    snod = getColumn(fname,5, delimiter=',', magnaprobe=False)
    #take the shortest freq for the ridges (to get the real depth)
    if 'ridge' in loc:
        #Date,Lon,Lat,X,Y,Snow,f1525Hz_hcp_i,f1525Hz_hcp_q,f5325Hz_hcp_i,f5325Hz_hcp_q,18325Hz_hcp_i,f18325Hz_hcp_q,f63025Hz_hcp_i,f63025Hz_hcp_q,f93075Hz_hcp_i,f93075Hz_hcp_q
        #it = getColumn(fname,6, delimiter=',', magnaprobe=False) 
        it = getColumn(fname,9, delimiter=',', magnaprobe=False)       #closer to real thickness, but still influenced by consolidation (has detection limit)
        it = getColumn(fname,13, delimiter=',', magnaprobe=False)       #consolidation can be seen in column 13 (63kHz q) and 15 (93kHz q)
    else:
        it = getColumn(fname,6, delimiter=',', magnaprobe=False)
    mxx = np.array(mxx,dtype=np.float)
    myy = np.array(myy,dtype=np.float)
    si = np.array(snod,dtype=np.float)
    ii = np.array(it,dtype=np.float)
    
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
    fig1.patch.set_facecolor('0.5')
    
    ax = fig1.add_subplot(111)
    ax.set_xlabel('Length (m)', fontsize=20)
    ax.set_title(title+datel[dd], fontsize=25)
    ax.set_ylabel('Distance from water surface (m)', fontsize=20)
    ax.tick_params(axis="x", labelsize=14)
    ax.tick_params(axis="y", labelsize=14)
    ax.set_facecolor('0.3')
    
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

    #it looks like they started somewhere else the last two times, still went same direction...
    if date=='20200330' or date=='20200426':
        fb = np.concatenate((fb[-215:],fb[:-215]))
        ii = np.concatenate((ii[-215:],ii[:-215]))
        si = np.concatenate((si[-215:],si[:-215]))
    
    #extension at the FR transect
    if date!='20200305' and loc == 'ridgeFR1':
        x = x+19    #to have co-inciding crests

        
    #extension of the Allies ridge
    if loc == 'ridgeA1':
        if date=='20200117' or  date=='20200228':
            x = x+18

    #plot with equilibrium
    ax.plot(x,fb,label='ice surface',c='k',ls=':')
    
    #ax.plot(fb-ii,label='ice bottom'+date)
    #ax.plot(fb+si,label='snow surface'+date)
    ax.fill_between(x, fb, fb-ii,alpha=.6, color=colors[1], label='ice')
    ax.fill_between(x, fb, fb+si,alpha=.6, color=colors[0], label='snow')

    ax.set_ylim(-8,1.8)
    ax.set_xlim(0,x[-2])        #beacause last MP value/coordinate is typically same as first (at large distance)
    ax.legend(fontsize=20,loc='lower left',fancybox=True,facecolor=colors[0],framealpha=.6)
    print(outname)
    fig1.savefig(outpath+outname,bbox_inches='tight', facecolor=fig1.get_facecolor(), edgecolor='none')

    #save all these data and try to overlay them in a multi-profile plot
    from scipy.signal import savgol_filter
    fb_hat = savgol_filter(fb, window, polyorder) # window size 51, polynomial order 3
    ii_hat = savgol_filter(ii, window, polyorder)
    si_hat = savgol_filter(si, window, polyorder)  
    
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
ax.set_facecolor('0.8')

for i in range(0,len(fb_list)):
    x=x_list[i]
    
    #use the same freeboard all the times
    #for a static feature e.g. cosolidating ridge, last measurement is best
    #for a deforming transect e.g. Nloop or Sloop each transect might be separate
    if loc == 'Sloop' or loc == 'Nloop':
        fb = fb_list[i]
    else:
        fb = fb_list[-1]
    
    #some (ridge) transects were getting longer (typically over level ice, so not much changes there...)
    if len(fb) < len(x):
        extra = len(x)-len(fb)
        fb = np.append(fb,fb_list[i][-extra:])
        
    #while some are getting shorter...
    if len(fb) > len(x):
        extra = len(fb)-len(x)
        fb = fb[:-extra]
    
    #ax.plot(x, fb,c='0.75')
    ax.plot(x, fb-ii_list[i],c=colors[i],label=datel[i]+' bottom')
    ax.plot(x, fb+si_list[i],c=colors[i])

x=x_list[-1]
ax.plot(x,fb,label='ice surface',c=colors[-1],ls=':')    
ax.fill_between(x, fb, fb-ii_list[-1],alpha=.3, color=colors[-1], label='ice')
ax.fill_between(x, fb, fb+si_list[-1],alpha=.3, color=colors[-2], label='snow')
    
#x=x_list[0]
#ax.plot(x,fb_list[0],label='ice surface',c='k')    

ax.set_ylim(-8,1.8)
if loc == 'ridgeA1':
    ax.set_ylim(-10.5,3)

if loc=='Sloop':
    ax.set_xlim(0,1500)
if loc=='Nloop':
    ax.set_xlim(0,1310)

#if loc=='special':
    #ax.set_ylim(-6,1.5)

ax.legend(fontsize=20,loc='lower left',fancybox=True,facecolor=colors[-1],framealpha=.1)
outname = 'profile_all_'+loc+'gridded.png'
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
    ax.set_xlim(0,1310)
ax.legend(fontsize=20,loc='upper right',fancybox=True,facecolor=colors[-1],framealpha=.1)
outname = 'profile_snow_'+loc+'ungridded.png'
fig3.savefig(outpath+outname,bbox_inches='tight')

