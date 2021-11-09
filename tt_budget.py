import numpy as np
from glob import glob
from tt_func import getColumn
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

#PDFs for winter heat budget
inpath_grid = '../data/grids_AGU/'
inpath_table = '../data/MCS/MP/'
outpath = '../plots_AGU/'
outname = 'pdf_budget.png'

locs = ['Nloop','Sloop','snow1','runway','special','special','special','special']
dates= ['20200130','20200130','20200126','20200207','20200123','20200126','20200107','20200115']
irbins = np.arange(0,6,.06)

i=0
snod=[]
it=[]
ss_mean=[]
ii_mode=[]
for loc in locs:
    print(loc)
    date = dates[i]
    
    #load the csv data created in tt_grid.py
    fname = glob(inpath_table+'*/magna+gem2-transect-'+date+'*'+loc+'*.csv')[0]
    ss = getColumn(fname,5, delimiter=',')
    ii = getColumn(fname,8, delimiter=',')
    
    ss_mean.append(np.mean(np.array(ss,dtype=np.float)))
    
    tmp = np.array(ii,dtype=np.float)
    it_pos = np.ma.array(tmp,mask=it==0);it_pos=it_pos.compressed()  #take only non-zero (not detected as negative) values
    hist = np.histogram(it_pos,bins=irbins)
    srt = np.argsort(hist[0])                           #indexes that would sort the array
    mm = srt[-1]                                        #same as: np.argmax(hist[0])
    mm1 = np.argmax(hist[0])
    mo = (hist[1][mm] + hist[1][mm+1])/2           #take mean of the bin for the mode value
    ii_mode.append(mo)
    
    snod.extend(ss)
    it.extend(ii)
    
    
    i=i+1

snod = np.array(snod,dtype=np.float)
it = np.array(it,dtype=np.float)

#append a 50m open water lead?

    
#colors = plt.cm.rainbow(np.linspace(0, 1, len(dates)))

#PDFs
fig1 = plt.figure(figsize=(15,6))
#fig1.suptitle(title, fontsize=30)
ax = fig1.add_subplot(121)
#ax.set_title('S transect loop')
ymax=.15
ax.set_ylim(0,ymax)
ax.set_xlabel('Snow depth (m)', fontsize=20)
ax.set_ylabel('Probability', fontsize=20)
srbins = np.arange(0,.8,.02)
ax.tick_params(axis="x", labelsize=14)
ax.tick_params(axis="y", labelsize=14)
ax.set_xlim(0,.8)

bx = fig1.add_subplot(122)
#bx.set_title('S transect loop')
ymax=.15
bx.set_ylim(0,ymax)
bx.set_xlabel('Ice thickness (m)', fontsize=20)
bx.set_ylabel('Probability', fontsize=20)
bx.tick_params(axis="x", labelsize=14)
bx.tick_params(axis="y", labelsize=14)
bx.set_xlim(0,6)
    
#means and modes
mn = np.mean(np.ma.masked_invalid(snod).compressed())#.compressed()
print(mn)
    
#find mode
it_pos = np.ma.array(it,mask=it==0);it_pos=it_pos.compressed()  #take only non-zero (not detected as negative) values
hist = np.histogram(it_pos,bins=irbins)
srt = np.argsort(hist[0])                           #indexes that would sort the array
mm = srt[-1]                                        #same as: np.argmax(hist[0])
mm1 = np.argmax(hist[0])
mo = (hist[1][mm] + hist[1][mm+1])/2           #take mean of the bin for the mode value
print(mo)
mni=np.mean(it_pos)

#plot PDFs
weights = np.ones_like(snod) / (len(snod))
n, bins, patches = ax.hist(snod, srbins, histtype='step', color='b', linewidth=4, alpha=.5, weights=weights)
ax.plot([mn,mn],[0,ymax],c='b',ls='--', label='mean = '+str(round(mn,2))+' m')

weights = np.ones_like(it) / (len(it))
n, bins, patches = bx.hist(it, irbins, histtype='step', color='g', linewidth=4, alpha=.5, weights=weights)
bx.plot([mo,mo],[0,ymax],c='g',ls='--', label='mode = '+str(round(mo,2))+' m')
bx.plot([mni,mni],[0,ymax],c='k',ls=':', label='mean = '+str(round(mni,2))+' m')


for i in range(0,len(locs)):
    print(locs[i])
    mn=ss_mean[i]
    ax.plot([mn,mn],[0,ymax],c='r',ls=':')
    
    mo=ii_mode[i]
    bx.plot([mo,mo],[0,ymax],c='r',ls=':')

print(outname)
ax.legend(fontsize=20)
bx.legend(fontsize=20)

fig1.savefig(outpath+outname,bbox_inches='tight')
