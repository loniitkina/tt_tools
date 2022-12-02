import numpy as np
from glob import glob
from tt_func import getColumn
import matplotlib.pyplot as plt
from datetime import datetime

inpath = '../data/MCS/MP/'
locs = ['Nloop','Sloop','snow1','runway','transect','albedoRBB','albedoLD','albedoK','kuka','ARIEL','special','ridge*']
locnames = ['Nloop','Sloop','Snow1','Runway','Transect','AlbedoRBB','AlbedoLD','AlbedoK','Kuka','Ariel','Special','Ridge']

#cols = plt.cm.Paired(np.linspace(0, 1, len(locs)))

#colors matching the map
cols = ['salmon','purple','gold','deeppink','orange','cornflowerblue','indigo','m','k','r','c','limegreen']

#markers
mrk = ['v','v','v','v','s','s','D','*','*','*','o','X']

outpath='../plots_revision/'
outname='stats_updt.png'

#Timeseries scatter plot
fig1 = plt.figure(figsize=(20,6))
fig1.patch.set_facecolor('0.5')
ax = fig1.add_subplot(121)
bx = fig1.add_subplot(122)
ax.set_ylabel('Transect Length (m)', fontsize=20)
ax.tick_params(axis="x", labelsize=14)
ax.tick_params(axis="y", labelsize=14)
ax.set_ylim(0,4000)

#bx.set_xlabel('Time', fontsize=20)
#bx.set_title(title, fontsize=25)
bx.set_ylabel('Measurement spacing (m)', fontsize=20)
bx.tick_params(axis="x", labelsize=14)
bx.tick_params(axis="y", labelsize=14)
##bx.set_facecolor('0.3')
#bx.set_xlim(0,1)
bx.set_ylim(0,5)

total_l=0
total_n=0

for loc in range(0,len(locs)):
    #get list of all files for listed locations
    flist = sorted(glob(inpath+'*/*_PS122*'+locs[loc]+'-meta.txt'))

    for fn in flist:
        #print(fn)
        
        #get dates from file names
        datem = fn.split('-')[-4].split('_')[0]
        date = datetime.strptime(datem, '%Y%m%d')
        
        #open files
        with open(fn) as f:
            content = f.readlines()
        f.close()
        
        #read spacing and total length
        ll=float(content[0])
        ss=float(content[1])
        
        #GPS problem on MP
        if locs[loc] == 'snow1' and datem=='20200223':
            ll = 400.
            ss = 400./276   #Ian only took 276 valid MP measurements (compared to normal ~450)
            
        #off the scale
        if locs[loc] == 'special' and datem=='20200123':
            print('long transect is %i m long' %(ll))
                                
        #plot dates vs total length
        if fn != flist[0]:
            ax.scatter(date,ll,marker=mrk[loc],s=70,c=cols[loc],alpha=.8)
        else:    
            ax.scatter(date,ll,marker=mrk[loc],s=70,c=cols[loc],alpha=.8,label=locnames[loc])
        
        #plot dates vs spacings
        if fn != flist[0]:
            bx.scatter(date,ss,marker=mrk[loc],s=70,c=cols[loc],alpha=.8)
        else:
            bx.scatter(date,ss,marker=mrk[loc],s=70,c=cols[loc],alpha=.8,label=locnames[loc])

        
        total_l = total_l+ll
        total_n = total_n+int(ll/ss)

#shade the COs?



#print total length of all MOSAiC transects:
print('Total length (km) of all MOSAiC transects')
print(total_l/1000)
print('Total number of all MOSAiC MP measurements')
print(total_n)

ax.legend(fontsize=15,fancybox=True,framealpha=.9,ncol=2,loc='upper left')

#dates for the publisher
from matplotlib.dates import MonthLocator, DateFormatter
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
ax.xaxis.set_minor_locator(MonthLocator())
ax.xaxis.set_major_formatter(DateFormatter('%b %Y'))

bx.xaxis.set_minor_locator(MonthLocator())
bx.xaxis.set_major_formatter(DateFormatter('%b %Y'))

fig1.autofmt_xdate()
#plt.show()

fig1.savefig(outpath+outname,bbox_inches='tight')



