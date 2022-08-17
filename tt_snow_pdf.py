import numpy as np
from glob import glob
from tt_func import getColumn
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

#PDFs for winter heat budget
inpath_grid = '../data/grids_AGU/'
inpath_table = '../data/MCS/MP/'
outpath = '../plots_revision/'

outname = 'pdf_snow_comp.png'

#selection of transects
locs = ['runway','special','Nloop','Sloop','runway','special']
dates= ['20200112','20200123','20200130','20200130','20200207','20200617']

locs = ['runway','Nloop','Sloop','runway','special']
dates= ['20200112','20200130','20200130','20200207','20200617']

dt = [ datetime.strptime(x, '%Y%m%d') for x in dates ]
datel = [ datetime.strftime(x, '%B %d %Y') for x in dt ]

cols = plt.cm.rainbow(np.linspace(0, 1, len(dates)))


srbins = np.arange(0,1,.02)

#PDFs
fig1 = plt.figure(figsize=(20,10))
#fig1.suptitle(title, fontsize=30)
ax = fig1.add_subplot(121)
ax.text(-.13, .355, "a", ha="center", va="center", size=45)  #make simple figure annotation
ax.set_xlabel('Snow depth (m)', fontsize=25)
ax.set_ylabel('Probability', fontsize=25)
ax.tick_params(axis="x", labelsize=20)
ax.tick_params(axis="y", labelsize=20)
ax.set_xlim(0,1)
#ax.set_ylim(0,0.35)

bx = fig1.add_subplot(122)
bx.text(-.13, .11, "b", ha="center", va="center", size=45)  #make simple figure annotation
bx.set_xlabel('Snow depth (m)', fontsize=25)
bx.set_ylabel('Probability', fontsize=25)
bx.tick_params(axis="x", labelsize=20)
bx.tick_params(axis="y", labelsize=20)
bx.set_xlim(0,1)


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
    if date=='20200617':
        fname = glob(inpath_table+'*/magna+gem2-transect-'+date+'*'+loc+'*.csv')[1]
        #separate FYI and SYI surfaces on this initial survey
        #all data with y<800
        print(fname)
        yy = getColumn(fname,4, delimiter=',')
        yy = np.array(yy,dtype=np.float)
        fyi_mask=yy<-800
        
    ss = getColumn(fname,5, delimiter=',')
    ii = getColumn(fname,8, delimiter=',')

    snod = np.array(ss,dtype=np.float)
    it = np.array(ii,dtype=np.float)



    
    if date=='20200617':
        
        weights = np.ones_like(snod) / (len(snod))
        n, bins, patches = bx.hist(snod, srbins, histtype='step', color=cols[i], linewidth=4, alpha=.5, weights=weights,label='Initial - '+datel[i])
        #ax.plot([mn,mn],[0,ymax],c='b',ls='--', label='mean = '+str(round(mn,2))+' m')
        print(len(snod))
        
        snod_fyi=np.ma.array(snod,mask=~fyi_mask).compressed()
        weights = np.ones_like(snod_fyi) / (len(snod_fyi))
        n, bins, patches = bx.hist(snod_fyi, srbins, histtype='step', color='b', linewidth=4, alpha=.5, weights=weights,label='Initial FYI - '+datel[i])
        print(len(snod_fyi))
        
        snod_syi=np.ma.array(snod,mask=fyi_mask).compressed()
        weights = np.ones_like(snod_syi) / (len(snod_syi))
        n, bins, patches = bx.hist(snod_syi, srbins, histtype='step', color='m', linewidth=4, alpha=.5, weights=weights,label='Initial SYI - '+datel[i])
        print(len(snod_syi))
        exit()
    
    else:
        #plot PDFs
        weights = np.ones_like(snod) / (len(snod))
        label = locs[i]+' - '+datel[i]
        if locs[i]=='runway':
            label = 'Runway - '+datel[i]
        if date=='20200123': label='long '+datel[i]
        n, bins, patches = ax.hist(snod, srbins, histtype='step', color=cols[i], linewidth=4, alpha=.5, weights=weights,label=label)
        #ax.plot([mn,mn],[0,ymax],c='b',ls='--', label='mean = '+str(round(mn,2))+' m')
        
    
    i=i+1
    
#for i in range(0,len(locs)):
    #print(locs[i])
    #mn=ss_mean[i]
    #ax.plot([mn,mn],[0,ymax],c='r',ls=':')
    
    #mo=ii_mode[i]
    #bx.plot([mo,mo],[0,ymax],c='r',ls=':')

print(outname)
ax.legend(fontsize=20)
bx.legend(fontsize=20)

fig1.savefig(outpath+outname,bbox_inches='tight')
