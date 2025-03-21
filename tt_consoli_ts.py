import numpy as np
from glob import glob
from tt_func import getColumn, running_stats
from scipy.signal import savgol_filter
from datetime import datetime
import matplotlib.pyplot as plt

#Allie's Ridge level ice is actually not measured. Use Nloop modal thickness for LI and do not plot any snow depth over level ice (just over ridge). In discussion we cna say that the level ice thickness from Nloop is the same as for the AR.

locs = ['Sloop','Nloop','transect','ridgeFR1','ridgeFR2','ridgeFR3','ridgeA1','ridgeA2','ridgeA3']
locs_rov = ['ridgeFR1','ridgeFR2','ridgeFR3','ridgeA1','ridgeA2','ridgeA3']
cols = ['purple','salmon','gold','deeppink','r','cornflowerblue','k','m','limegreen']

import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

#MOSAiC
inpath_table = '../data/ridges_multif/'
outpath = '../plots_ridges/'

fig1, ax = plt.subplots(4, 1,gridspec_kw={'height_ratios': [1,1,.5,1]},figsize=(10,40))

ax[0].set_ylabel('Thickness (m)')
ax[0].set_ylim(1,9)

ax[1].set_ylabel('CL/LI thickness')

ax[3].set_ylabel('Snow depth (m)')
ax[3].set_ylim(0,1.2)

ax[2].set_ylabel('Ice drift speed (m/s)',c='0.5')
ax[2].set_ylim(0,.6)

fig2 = plt.figure(figsize=(16,5))
bx = fig2.add_subplot(131)
cx = fig2.add_subplot(132)
dx = fig2.add_subplot(133)

als_fb=[]

for i in range(0,len(locs)):
    loc = locs[i]
    col = cols[i]
    fname = inpath_table+loc+'_cc.csv'
    print(fname)
    if loc=='transect': loc='MeltMix'
    
    dates = getColumn(fname,0); print(dates)
    dt = [ datetime.strptime(x, '%Y-%m-%d %H:%M:%S') for x in dates ]
    
    mean_si_list = getColumn(fname,1)
    si = np.array(mean_si_list,dtype=np.float)
    
    mean_ii_list = getColumn(fname,2)
    ii = np.array(mean_ii_list,dtype=np.float)
    
    mean_cc_list = getColumn(fname,3)
    cc = np.array(mean_cc_list,dtype=np.float)
    
    modes = getColumn(fname,4)
    li = np.array(modes,dtype=np.float)
    #special cases for Allie's Ridge to match the modal thickness to Nloop
    #Nloop: [0.63 0.63 1.05 1.17 1.29 1.35 1.41 1.53 1.65 1.77 1.83 1.71]
    #[2019-11-28,2019-12-05,2020-01-02,2020-01-09,2020-01-30,'2020-02-20','2020-03-05','2020-03-20','2020-04-03','2020-04-24','2020-04-30','2020-05-07]
    if loc=='ridgeA1': li=np.array([1.29,1.35,1.41,1.77,1.7])
    if loc=='ridgeA2': li=np.array([1.41,1.53,1.77,1.7])
    if loc=='ridgeA3': li=np.array([1.41,1.53,1.77,1.7])
    #also the MeltMix
    if loc=='MeltMix': li=np.array([1.7, 1.7, 1.7, 1.7, 1.7])
    
    si_mo = getColumn(fname,5)
    si_mo = np.array(si_mo,dtype=np.float)

    #consolidation
    ratio_c = cc / li
    print(ratio_c)
    
    #snow ratio between level ice and ridges 
    ratio_s = si / si_mo
    
    if loc in locs_rov:
        mean_fb_list = getColumn(fname,6)
        fb = np.array(mean_fb_list,dtype=np.float)
        
        mean_fb_hs_list = getColumn(fname,7)
        fb_hs = np.array(mean_fb_hs_list,dtype=np.float)
        
        max_fb_list = getColumn(fname,8)
        max_fb = np.array(max_fb_list,dtype=np.float)
        
        max_fb_hs_list = getColumn(fname,9)
        max_fb_hs = np.array(max_fb_hs_list,dtype=np.float)
        
        #only the first one is relevant
        bx.plot(fb[0],fb_hs[0],'o',c=col,label=loc)
        
        cx.plot(max_fb[0],max_fb_hs[0],'o',c=col,label=loc)
        
        #keep for shape ratio
        als_fb.append(fb[0])
    

    #ax.plot(dt,si,'o',label='snow depth'+loc)
    ax[0].plot(dt,ii,'x',ls='--',c=col)
    ax[0].plot(dt,cc,'o',ls='-',c=col,label=loc)
    #if loc not in ['ridgeA1','ridgeA2','ridgeA3']:
        #ax[2].plot(dt,li,'v',ls=':',c=col)
        
    
    #ax2.plot(dt,ratio_p,'o',ls='-',c=col,label=loc)
    #if loc not in ['ridgeA1','ridgeA2','ridgeA3']:
    ax[1].plot(dt,ratio_c,'o',ls='-',c=col)
        #ax[3].plot(dt,ratio_s,'s',ls='--',c=col)
    ax[3].plot(dt,si,'o',ls='--',c=col)
    if loc not in ['ridgeA1','ridgeA2','ridgeA3']:
        ax[3].plot(dt,si_mo,'^',ls='-',c=col)
    

    #ax.plot(dt[1:],ds,'s',label='snow erosion/deposition')
    #ax.plot(dt[1:],dr,'x',label='consolidation change')     

#get buoy velocity time series
inpath = '../data/mosaic_buoy_data/selection/'

#flist= glob(inpath+'2019P*_locs.csv')

#buoys
buoys = glob(inpath+'2019P103*_proc.csv')

for buoy in buoys:
    #print(buoy)
    time = getColumn(buoy,0)
    dtb = [ datetime.strptime(time[x], "%Y-%m-%dT%H:%M:%S") for x in range(len(time)) ]
    drift = np.asarray(getColumn(buoy,3),dtype=float)
    
    #smooth the drift speed
    window=51; polyorder=3
    drift = savgol_filter(drift, window, polyorder) # window size 51, polynomial order 
    
    ax[2].plot(dtb,drift,c='0.5',lw=1)
    ax[2].axhline(y=0.2,c='0.5',ls='--')
    
    for aa in [ax[0],ax[1],ax[2],ax[3]]:
        aa.axvspan(datetime(2019,12,5), datetime(2020,3,12),color='gold',alpha=.1)         #winter low drift period
        aa.axvspan(datetime(2020,5,15), datetime(2020,6,12),color='pink',alpha=.2)         #melt period low drift periods
        aa.axvspan(datetime(2020,6,17), datetime(2020,7,2),color='limegreen',alpha=.1)
        aa.axvspan(datetime(2020,7,12), datetime(2020,7,17),color='blue',alpha=.1)

#weather
inpath='../data/SnowModel/final/'
fname = inpath+'final_10m_3hrly_met_2023_02_14.dat'
print(fname)

import csv
import re
from datetime import timedelta
results = csv.reader(open(fname))
#get rid of all multi-white spaces and split in those that remain
results_clean = [re.sub(" +", " ",row[0]) for row in results]

#temperature, humidity, wind speed, wind direction, precipitation

tair_model = [row.split(" ")[3] for row in results_clean]
tair_model = np.array(tair_model,dtype=np.float)     
tair_model = np.ma.array(tair_model,mask=tair_model==-9999)

#dates
numdays=366*8
start = datetime(2019,8,1)
dt = [start + timedelta(hours=x*3) for x in range(numdays)]

ax3 = ax[2].twinx()
ax3.set_ylabel('Air temperature',c='darkred')
ax3.plot(dt,tair_model,c='darkred',lw=1)
ax3.axhline(y=0,c='darkred',ls='--')

ax[0].legend(ncol=9,loc='upper right')
for aa in [ax[0],ax[1],ax[2],ax[3]]:
    aa.set_xlim(datetime(2019,11,25),datetime(2020,7,31))

#make simple figure annotation
xi=datetime(2019,12,1)
ax[0].text(xi, 8, "a", ha="center", va="center", size=20)
ax[1].text(xi, 4, "b", ha="center", va="center", size=20)
ax[3].text(xi, 1, "c", ha="center", va="center", size=20)
ax[2].text(xi, .45, "d", ha="center", va="center", size=20)


bx.set_xlim(0,1)
bx.set_ylim(0,1)
bx.set_xlabel('ALS freeboard (m)', fontsize=20)
bx.set_ylabel('hydrostatic freeboard (m)', fontsize=20)
bx.legend()

cx.set_xlim(0,2.55)
cx.set_ylim(0,2.55)
cx.set_xlabel('max ALS freeboard (m)', fontsize=20)
cx.set_ylabel('max hydrostatic freeboard (m)', fontsize=20)
#cx.legend()

fname = inpath_table+'ridge_sail_keel_w.csv'
#print(fname)
name = getColumn(fname,0)
sail = getColumn(fname,2); sail = np.array(sail,dtype=np.float)
keel = getColumn(fname,3); keel = np.array(keel,dtype=np.float)
ratio = sail/keel

for i in range(0,len(name)):
    col=cols[i+3]
    dx.plot(als_fb[i],ratio[i],'o',c=col,label=name[i])

dx.set_xlabel('ALS freeboard (m)', fontsize=20)
dx.set_ylabel('sail/keel width ratio', fontsize=20)
#dx.legend()

##add transect paper data (modal sea ice thickness)
#inpath_mosaic='../data/MCS/MP/'
#locs = ['Sloop','Nloop','transect']

#for i in range(0,len(locs)):
    #loc = locs[i]
    #col = cols[i]
    #fname=inpath_mosaic+'ts_'+loc+'_1m_gridded.csv' #produced by 
    #print(fname)
    
    #dt1= getColumn(fname,0)
    #m_snow= getColumn(fname,1)
    #std_snow= getColumn(fname,2)
    #m_ice= getColumn(fname,3)
    #std_ice= getColumn(fname,4)
    #mo_ice= getColumn(fname,5)
    #dt = [ datetime.strptime(x, '%Y%m%d') for x in dt1 ]
    #m_snow = np.array(m_snow,dtype=np.float)
    #std_snow = np.array(std_snow,dtype=np.float)
    #m_ice = np.array(m_ice,dtype=np.float)
    #std_ice = np.array(std_ice,dtype=np.float)
    #mo_ice = np.array(mo_ice,dtype=np.float)
    
    ##ax[0].plot(dt,mo_ice,'v',ls=':',c=col)


plt.show()
outname='transect_consoli'
fig1.savefig(outpath+outname,bbox_inches='tight')

outname='transect_fb'
fig2.savefig(outpath+outname,bbox_inches='tight')
