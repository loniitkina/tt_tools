import numpy as np
from glob import glob
from tt_func import getColumn
import matplotlib.pyplot as plt
from datetime import datetime



inpath = '../data/MCS/MP/'
locs = ['Nloop','Sloop','transect','ridge*','snow1','runway','special','albedoRBB','albedoLD']
cols = ['r','b','m','g','y','c','k','royalblue','hotpink']


#Timeseries scatter plot
fig1 = plt.figure(figsize=(10,10))
fig1.patch.set_facecolor('0.5')
ax = fig1.add_subplot(211)
bx = fig1.add_subplot(212)
ax.set_ylabel('Transect Lenght (m)', fontsize=20)
bx.set_xlabel('Time', fontsize=20)
#bx.set_title(title, fontsize=25)
bx.set_ylabel('Measurement spacing (m)', fontsize=20)
bx.tick_params(axis="x", labelsize=14)
bx.tick_params(axis="y", labelsize=14)
##bx.set_facecolor('0.3')
#bx.set_xlim(0,1)
#bx.set_ylim(0,2)



for loc in range(0,len(locs)):
    #get list of all files for listed locations
    flist = sorted(glob(inpath+'*/*'+locs[loc]+'-meta.txt'))

    for fn in flist:
        print(fn)
        
        datem = fn.split('-')[-4].split('_')[0]
        date = datetime.strptime(datem, '%Y%m%d')
        
        with open(fn) as f:
            content = f.readlines()
        f.close()
        
        ll=float(content[0])
        ss=float(content[1])
        
        #GPS problem on MP
        if locs[loc] == 'snow1' and datem=='20200223':
            ll = 400.
            ss = 1.
        
        if fn == flist[0]:
            ax.scatter(date,ll,c=cols[loc],label=locs[loc])
        else:
            ax.scatter(date,ll,c=cols[loc])
        bx.scatter(date,ss,c=cols[loc])
        
        

ax.legend()
fig1.autofmt_xdate()
plt.show()

#get dates from file names

#open files

#read spacing and total lenght

#plot dates vs total lenght

#plot dates vs spacings
