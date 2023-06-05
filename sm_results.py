import csv
import re
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from tt_func import getColumn


inpath='../data/SnowModel/final/'
outpath='../plots_sm/'

locs = ['Nloop','Sloop','Runwy']
#locs = ['Nloop']
ls = ['-','--',':']
cols = ['royalblue','purple','teal']

numdays=366*8
start = datetime(2019,8,1)
dt = [start + timedelta(hours=x*3) for x in range(numdays)]
end = datetime(2020,8,1)

fig1 = plt.figure(figsize=(10,10))
ax = fig1.add_subplot(111)

for i in range(0,len(locs)):
    loc = locs[i]
    #fname = inpath+'snow_tice_'+loc+'_2023_02_14.dat'# 24 Aug, rks = 9.0 * sm_cond, init=5cm
    #fname = inpath+'snow_tice_'+loc+'_2023_06_02k.dat'# 15 Aug, rks = 8.0 * sm_cond, init=20cm
    #fname = inpath+'snow_tice_'+loc+'_2023_06_02l.dat'# 1 Aug, rks = 8.0 * sm_cond, init=30cm
    #fname = inpath+'snow_tice_'+loc+'_2023_06_02m.dat'# 1 Aug, rks = 6.0 * sm_cond, init=30cm
    #fname = inpath+'snow_tice_'+loc+'_2023_06_02n.dat' #Amy's parametrization
    #fname = inpath+'snow_tice_'+loc+'_2023_06_02p.dat' #rks = 0.32, mean for the models - still WAY too low!
    #fname = inpath+'snow_tice_'+loc+'_2023_06_02r.dat' # 24 Aug, rks = 5.0 * sm_cond, init=30cm
    fname = inpath+'snow_tice_'+loc+'_2023_06_02.dat' # 24 Aug, rks = 6.0 * sm_cond, init=40cm
    #fname = inpath+'snow_tice_'+loc+'_2023_06_02_low.dat'   #low snow depth
    
    #HEADER
    #iter,swed_mod1,swed_mod2,snod,sden,dyn_corr,tice,swed_obs,sden_obs,snod_obs,timo_obs
    
    results = csv.reader(open(fname))
    #get rid of all multi-white spaces and split in those that remain
    results_clean = [re.sub(" +", " ",row[0]) for row in results]

    snod = [row.split(" ")[4] for row in results_clean]
    snod = np.array(snod,dtype=np.float)     
    snod = np.ma.array(snod,mask=snod==-9999)
    
    #Q&D fix for the density problem in the Sloop
    #read also snow density. If the snow density == 50, then modify the snow depth
    #for example: calculate the swe again and use density=2020
    sden = [row.split(" ")[5] for row in results_clean]
    sden = np.array(sden,dtype=np.float)     
    sden = np.ma.array(sden,mask=sden==-9999)
    
    
    snod[sden<155]=snod[sden<155.]/5
    
    tice = [row.split(" ")[7] for row in results_clean]
    tice = np.array(tice,dtype=np.float)     
    tice = np.ma.array(tice,mask=tice==-9999)
    
    so = [row.split(" ")[10] for row in results_clean]
    so = np.array(so,dtype=np.float)     
    so = np.ma.array(so,mask=so==-9999)
    
    io = [row.split(" ")[11] for row in results_clean]
    io = np.array(io,dtype=np.float)     
    io = np.ma.array(io,mask=io==-9999)
    
    #fig1 = plt.figure(figsize=(10,10))
    #ax = fig1.add_subplot(111)

    if loc=='Nloop':
        ax.plot(dt,snod, lw=3, ls=ls[i], c='turquoise', label='SnowModel snow')
        ax.plot(dt,np.zeros_like(snod),':k')
        ax.plot(dt,tice, lw=3, ls=ls[i], c='cornflowerblue', label='HIGHTSI ice')
        
    else:
        ax.plot(dt,snod, lw=3, ls=ls[i], c='turquoise')
        ax.plot(dt,np.zeros_like(snod),':k')
        ax.plot(dt,tice, lw=3, ls=ls[i], c='cornflowerblue')

    ax.plot(dt,so,'x', markeredgewidth=3, c=cols[i], ms=8, label='Transect '+loc)
    ax.plot(dt,io,'x', markeredgewidth=3, c=cols[i], ms=8)
    

    ax.legend(fontsize=18,loc='lower left')

    ax.set_ylabel('Ice thickness/Snow depth (m)',fontsize=20) # Y axis data label

    ax.set_xlim(datetime(2019,9,1),datetime(2020,7,29))

    ax.tick_params(axis="x", labelsize=14)
    ax.tick_params(axis="y", labelsize=14)

fig1.autofmt_xdate()

fig1.savefig(outpath+'sm_season_MOSAiC',bbox_inches='tight')
plt.show()


