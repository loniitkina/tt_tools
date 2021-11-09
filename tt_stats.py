import numpy as np
from glob import glob
from tt_func import getColumn
import matplotlib.pyplot as plt
from datetime import datetime

inpath = '../data/MCS/MP/'
locs = ['Nloop','Sloop','transect','ridge*','snow1','runway','albedoRBB','albedoLD','albedoK','kuka','ARIEL','special']

#cols = plt.cm.Paired(np.linspace(0, 1, len(locs)))

#colors matching the map
cols = ['salmon','purple','orange','limegreen','gold','deeppink','hotpink','cornflowerblue','m','k','r','c']

outpath='../plots_AGU/'
outname='stats.png'

#Timeseries scatter plot
fig1 = plt.figure(figsize=(20,6))
fig1.patch.set_facecolor('0.5')
ax = fig1.add_subplot(121)
bx = fig1.add_subplot(122)
ax.set_ylabel('Transect Lenght (m)', fontsize=20)
ax.tick_params(axis="x", labelsize=14)
ax.tick_params(axis="y", labelsize=14)
ax.set_ylim(0,5400)

#bx.set_xlabel('Time', fontsize=20)
#bx.set_title(title, fontsize=25)
bx.set_ylabel('Measurement spacing (m)', fontsize=20)
bx.tick_params(axis="x", labelsize=14)
bx.tick_params(axis="y", labelsize=14)
##bx.set_facecolor('0.3')
#bx.set_xlim(0,1)
bx.set_ylim(0,6)

total_l=0
total_n=0

for loc in range(0,len(locs)):
    #get list of all files for listed locations
    flist = sorted(glob(inpath+'*/*_PS122*'+locs[loc]+'-meta.txt'))

    for fn in flist:
        print(fn)
        
        #get dates from file names
        datem = fn.split('-')[-4].split('_')[0]
        date = datetime.strptime(datem, '%Y%m%d')
        
        #open files
        with open(fn) as f:
            content = f.readlines()
        f.close()
        
        #read spacing and total lenght
        ll=float(content[0])
        ss=float(content[1])
        
        #GPS problem on MP
        if locs[loc] == 'snow1' and datem=='20200223':
            ll = 400.
            ss = 400./276   #Ian only took 276 valid MP measurements (compared to normal ~450)
                                
        #plot dates vs total lenght
        ax.scatter(date,ll,c=cols[loc],alpha=.8)
        
        #plot dates vs spacings
        if fn != flist[0]:
            bx.scatter(date,ss,c=cols[loc],alpha=.8)
        else:
            bx.scatter(date,ss,c=cols[loc],alpha=.8,label=locs[loc])

        
        total_l = total_l+ll
        total_n = total_n+int(ll/ss)

#shade the COs?



#print total lenght of all MOSAiC transects:
print('Total lenght (km) of all MOSAiC transects')
print(total_l/1000)
print('Total number of all MOSAiC MP measurements')
print(total_n)

bx.legend(fontsize=13,fancybox=True,framealpha=.9,ncol=4,loc='upper left')
fig1.autofmt_xdate()
#plt.show()

fig1.savefig(outpath+outname,bbox_inches='tight')



