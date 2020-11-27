import numpy as np
from glob import glob
from tt_func import getColumn
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

#select location
loc = 'Nloop'
#loc = 'Sloop'
#loc = 'both'
#loc = 'snow1'
print(loc)

title='Southern transect loop'
title='Northern transect loop'

##two dates
#dates = ['20191219','20200220']
#dates = ['20191226','20200220']
#dates = ['20200102','20200220'] #platelet ice paper
#dates = ['20200112','20200207'] #gnss paper
dates = ['20191107','20200426'] #start and end of winter, S loop
dates = ['20191205','20200305'] #start and end of winter, N loop

#datel = ['2020/01/02','2020/02/20'] 
#datel = ['2020/01/12','2020/02/07']

#colors = ['blue','green']

#outname = 'pdf_'+loc+'_early26.png'
#outname = 'pdf_'+loc+'_platelet.png'
#outname = 'pdf_'+loc+'_gnss.png'

#all dates
#dates = ['20191107','20191114','20191205','20191226','20200102','20200109','20200130','20200206','20200220','20200227','20200305','20200330','20200426'] #Sloop
dates = ['20191107','20191114','20191205','20191219','20200102','20200109','20200130','20200206','20200220','20200227','20200305','20200416','20200430'] #Nloop

colors = plt.cm.rainbow(np.linspace(0, 1, len(dates)))
datel=dates
outname = 'pdf_'+loc+'_all.png'
outname_ts = 'ts_'+loc+'_all.png'
outname_ts_type = 'ts_'+loc+'_type.png'

##events (selected dates from leg 1-3)
#dates = ['20191107','20191205','20200227','20200426'] #Sloop
#dates = ['20191107','20191205','20200227','20200430'] #Nloop

#colors = plt.cm.rainbow(np.linspace(0, 1, len(dates)))
#datel=dates
#outname = 'pdf_'+loc+'_events.png'

#grid spacing
stp = '5'

inpath_grid = '../data/grids_AGU/'
outpath = '../plots_AGU/'

#PDFs
fig1 = plt.figure(figsize=(20,10))
fig1.suptitle(title, fontsize=30)
ax = fig1.add_subplot(121)
#ax.set_title('S transect loop')
ymax=.11
ax.set_ylim(0,ymax)
ax.set_xlabel('Snow depth (m)', fontsize=20)
ax.set_ylabel('Probability', fontsize=20)
srbins = np.arange(0,.8,.01)
ax.tick_params(axis="x", labelsize=14)
ax.tick_params(axis="y", labelsize=14)
ax.set_xlim(0,.8)

bx = fig1.add_subplot(122)
#bx.set_title('S transect loop')
ymax=.5
bx.set_ylim(0,ymax)
bx.set_xlabel('Ice thickness (m)', fontsize=20)
bx.set_ylabel('Probability', fontsize=20)
irbins = np.arange(0,5,.06)
bx.tick_params(axis="x", labelsize=14)
bx.tick_params(axis="y", labelsize=14)
bx.set_xlim(0,5)




#store data for time series
ts_snow=[]
ts_ice=[]
ts_mo=[]
#level and deformed ice
ts_snow_l=[]
ts_snow_d=[]

i=0
for date in dates:
    print(date)

    #load all the gridded data created in tt_grid.py
    if loc == 'both':
        
        of = inpath_grid+'Nloop'+'_'+date+'_'+stp+'m.npz'
        data = np.load(of)
        snod1 = data['snow']
        it1 = data['ice']
        
        of = inpath_grid+'Sloop'+'_'+date+'_'+stp+'m.npz'
        data = np.load(of)
        snod2 = data['snow']
        it2 = data['ice']  
        
        snod = np.nan_to_num(snod1, nan=0)+np.nan_to_num(snod2, nan=0)
        it = np.nan_to_num(it1, nan=0)+np.nan_to_num(it2, nan=0)
        snod = np.ma.array(snod,mask=snod==0)
        it = np.ma.array(it,mask=it==0)
        
    else:   
        of = inpath_grid+loc+'_'+date+'_'+stp+'m.npz'
        print(of)
        data = np.load(of)
        snod = data['snow']
        it = data['ice']
     
        #get rid of nans
        snod = np.ma.masked_invalid(snod)
        it = np.ma.masked_invalid(it)
        
    snod = snod[snod.mask == False]
    it = it[it.mask == False]
    
    #means and modes
    mn = np.mean(snod)
    print(mn)
    #mni = np.mean(it)
    
    #find mode
    hist = np.histogram(it,bins=irbins)
    srt = np.argsort(hist[0])                           #indexes that would sort the array
    mm = srt[-1]                                        #same as: np.argmax(hist[0])
    mm1 = np.argmax(hist[0])
    mo = (hist[1][mm] + hist[1][mm+1])/2           #take mean of the bin for the mode value
    print(mo)
    
    #plot PDFs
    weights = np.ones_like(snod) / (len(snod))
    n, bins, patches = ax.hist(snod, srbins, facecolor=colors[i], alpha=0.3, weights=weights, label=datel[i])
    ax.plot([mn,mn],[0,ymax],c=colors[i],ls='--', label='mean = '+str(round(mn,2)))

    weights = np.ones_like(it) / (len(it))
    n, bins, patches = bx.hist(it, irbins, facecolor=colors[i], alpha=0.3, weights=weights, label=datel[i])
    bx.plot([mo,mo],[0,ymax],c=colors[i],ls='--', label='mode = '+str(round(mo,2)))
    #bx.plot([mni,mni],[0,ymax],c='k',ls=':', label='mean = '+str(round(mni,2)))
    
    #save data for time series
    ts_snow.append(snod)
    #if date=='20200206' and loc == 'Sloop': continue #bad data for GEM-2 
    ts_ice.append(it)
    ts_mo.append(mo)
    
    #separate deformed and level ice based on the mode
    #use this to separate the snow depth
    level_ice = (it>mo-.25) & (it<mo+.25)
    deformed_ice = (it>mo+.25)
    
    #level_ice = (it<2)
    #deformed_ice = (it>2.8)
    
    level_snow = np.ma.array(snod,mask=~level_ice)
    def_snow = np.ma.array(snod,mask=~deformed_ice)
    
    
    #scatter plots
    fig3 = plt.figure(figsize=(20,9))
    fig3.suptitle(date, fontsize=30)
    zx = fig3.add_subplot(121)
    zx.set_title('Level ice', fontsize=25)
    zx.set_xlabel('Ice thickness (m)', fontsize=20)
    zx.set_ylabel('Snow depth (m)', fontsize=20)
    zx.tick_params(axis="x", labelsize=16)
    zx.tick_params(axis="y", labelsize=16)

    zzx = fig3.add_subplot(122)
    zzx.set_title('Deformed ice', fontsize=25)
    zzx.set_xlabel('Ice thickness (m)', fontsize=20)
    zzx.set_ylabel('Snow depth (m)', fontsize=20)
    zzx.tick_params(axis="x", labelsize=16)
    zzx.tick_params(axis="y", labelsize=16)

    zx.scatter(it,level_snow,c=colors[0], alpha=0.5, s=30)
    zzx.scatter(it,def_snow,c=colors[0], alpha=0.5, s=30)
    
    outname_sc = 'scatter_'+loc+'_'+date+'.png'
    fig3.savefig(outpath+outname_sc,bbox_inches='tight')

    #for time series    
    level_snow = np.ma.compressed(level_snow)
    def_snow = np.ma.compressed(def_snow)

    ts_snow_l.append(level_snow)
    ts_snow_d.append(def_snow)

    i = i+1
    
ax.legend(fontsize=20)
bx.legend(fontsize=20)

print(outname)
fig1.savefig(outpath+outname,bbox_inches='tight')



#time series
fig2 = plt.figure(figsize=(20,10))
cx = fig2.add_subplot(211)
cx.set_title(title, fontsize=25)
cx.set_ylabel('Snow depth (m)', fontsize=20)
cx.tick_params(axis="x", labelsize=14)
cx.tick_params(axis="y", labelsize=14)
cx.set_ylim(0,.8)

dx = fig2.add_subplot(212)
dx.set_ylabel('Ice thickness (m)', fontsize=20)
dx.tick_params(axis="x", labelsize=14)
dx.tick_params(axis="y", labelsize=14)
dx.set_ylim(-0.5,11)
if loc=='Sloop': dx.set_ylim(0,4)

#spacing between the box plots
dt = [ datetime.strptime(x, '%Y%m%d') for x in dates ]
dt_diff = [ (x-dt[0]).days for x in dt ]

#this is a very ugly trick: positions needs at least len=2...
for i in range(0,len(dates)):
    cx.boxplot([ts_snow[i],ts_snow[i]], notch=True, showfliers=False, positions=[dt_diff[i],dt_diff[i]],widths=5,patch_artist=True,
               boxprops=dict(facecolor=colors[i],alpha=.4))

for i in range(0,len(dates)):
    dx.boxplot([ts_ice[i],ts_ice[i]], notch=True, showfliers=False, positions=[dt_diff[i],dt_diff[i]],widths=5,patch_artist=True,
               boxprops=dict(facecolor=colors[i],alpha=.4))
    
dx.plot(dt_diff,ts_mo,'s',ms=15, label='mode',c='0.3')

dx.legend(fontsize=20)

#and a dirty trick for the X axis
dates = ['20191101','20191201','20200101','20200201','20200301','20200401','20200501']
dt = [ datetime.strptime(x, '%Y%m%d') for x in dates ]
dt_diff = [ (x-dt[0]).days for x in dt ]
plt.xticks(dt_diff, ['1 Nov','1 Dec','1 Jan','1 Feb','1 Mar','1 Apr','1 May'])
fig2.autofmt_xdate()

fig2.savefig(outpath+outname_ts,bbox_inches='tight')

###time series of deformed/level snow and ice 
#fig4 = plt.figure(figsize=(20,5))
#cx = fig4.add_subplot(111)
#cx.set_title(title, fontsize=25)
#cx.set_ylabel('Snow depth (m)', fontsize=20)
#cx.tick_params(axis="x", labelsize=14)
#cx.tick_params(axis="y", labelsize=14)
#cx.set_ylim(0,1)

##spacing between the box plots
#dt = [ datetime.strptime(x, '%Y%m%d') for x in dates ]
#dt_diff = [ (x-dt[0]).days for x in dt ]
#dt_diff_off = [ (x-dt[0]).days+3 for x in dt ]

##snow on level ice
#bp1=cx.boxplot(ts_snow_l, notch=True, showfliers=False, positions=dt_diff,widths=3,patch_artist=True,
            #boxprops=dict(facecolor=colors[2],alpha=.4))

##snow in ridges
#bp2=cx.boxplot(ts_snow_d, notch=True, showfliers=False, positions=dt_diff_off,widths=3,patch_artist=True,
            #boxprops=dict(facecolor=colors[4],alpha=.4))

##and a dirty trick for the X axis
#dates = ['20191101','20191201','20200101','20200201','20200301','20200401','20200501']
#dt = [ datetime.strptime(x, '%Y%m%d') for x in dates ]
#dt_diff = [ (x-dt[0]).days for x in dt ]
#plt.xticks(dt_diff, ['1 Nov','1 Dec','1 Jan','1 Feb','1 Mar','1 Apr','1 May'])
#fig4.autofmt_xdate()

#cx.legend([bp1["boxes"][0], bp2["boxes"][0]], ['level ice', 'deformed ice'], loc='upper left', fontsize=20)

#fig4.savefig(outpath+outname_ts_type,bbox_inches='tight')

