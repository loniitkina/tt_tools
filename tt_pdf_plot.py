import numpy as np
from glob import glob
from tt_func import getColumn
import matplotlib.pyplot as plt

#two dates
dates = ['20191219','20200220']
dates = ['20191226','20200220']
#dates = ['20200102','20200220']

colors = ['blue','green']

#all dates
dates = ['20191226','20200102','20200109','20200130','20200206','20200220']

colors = ['darkred','blue','orange','purple','yellow','green']

#select location
loc = 'Nloop'
loc = 'Sloop'
loc = 'both'

print(loc)

#grid spacing
stp = '1'

inpath = '../data/'
inpath_grid = '../data/grids/'
outpath = '../plots/'

outname = 'pdf_'+loc+'.png'
outname = 'pdf_'+loc+'_early26.png'
outname = 'pdf_'+loc+'_all.png'

fig1 = plt.figure(figsize=(20,10))
ax = fig1.add_subplot(121)
#ax.set_title('S transect loop')
ymax=.1
ax.set_ylim(0,ymax)
ax.set_xlabel('Snow depth (m)')
srbins = np.arange(0,.8,.01)

bx = fig1.add_subplot(122)
#bx.set_title('S transect loop')
ymax=.15
bx.set_ylim(0,ymax)
bx.set_xlabel('Ice thickness (m)')
irbins = np.arange(0,5,.05)

i=0
for date in dates:
    print(date)

    #load all the gridded data
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
    
    #find mode
    hist = np.histogram(it,bins=irbins)
    srt = np.argsort(hist[0])                           #indexes that would sort the array
    mm = srt[-1]                                        #same as: np.argmax(hist[0])
    mm1 = np.argmax(hist[0])
    mo = (hist[1][mm] + hist[1][mm+1])/2           #take mean of the bin for the mode value
    print(mo)
    
    #plot
    weights = np.ones_like(snod) / (len(snod))
    n, bins, patches = ax.hist(snod, srbins, facecolor=colors[i], alpha=0.3, weights=weights, label=date)
    ax.plot([mn,mn],[0,ymax],c=colors[i],ls='--', label='mean = '+str(round(mn,2)))

    weights = np.ones_like(it) / (len(it))
    n, bins, patches = bx.hist(it, irbins, facecolor=colors[i], alpha=0.3, weights=weights, label=date)
    bx.plot([mo,mo],[0,ymax],c=colors[i],ls='--', label='mode = '+str(round(mo,2)))

    i = i+1
    
ax.legend()
bx.legend()

print(outname)
fig1.savefig(outpath+outname)

