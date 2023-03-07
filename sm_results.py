import csv
import re
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from tt_func import getColumn


inpath='../data/SnowModel/final/'
outpath='../plots_sm/'

locs = ['Nloop','Sloop','Runwy']

numdays=366*8
start = datetime(2019,8,1)
dt = [start + timedelta(hours=x*3) for x in range(numdays)]
end = datetime(2020,8,1)

for loc in locs:
    fname = inpath+'snow_tice_'+loc+'_2023_02_14.dat'
    #iter,swed_mod1,swed_mod2,snod,sden,dyn_corr,tice,swed_obs,sden_obs,snod_obs,timo_obs
    
    results = csv.reader(open(fname))
    #get rid of all multi-white spaces and split in those that remain
    results_clean = [re.sub(" +", " ",row[0]) for row in results]

    snod = [row.split(" ")[4] for row in results_clean]
    snod = np.array(snod,dtype=np.float)     
    snod = np.ma.array(snod,mask=snod==-9999)
    
    tice = [row.split(" ")[7] for row in results_clean]
    tice = np.array(tice,dtype=np.float)     
    tice = np.ma.array(tice,mask=tice==-9999)
    
    so = [row.split(" ")[10] for row in results_clean]
    so = np.array(so,dtype=np.float)     
    so = np.ma.array(so,mask=so==-9999)
    
    io = [row.split(" ")[11] for row in results_clean]
    io = np.array(io,dtype=np.float)     
    io = np.ma.array(io,mask=io==-9999)
    
    fig1 = plt.figure(figsize=(10,10))
    ax = fig1.add_subplot(111)

    ax.plot(dt,snod, lw=5, c='turquoise', label='SnowModel snow')
    ax.plot(dt,np.zeros_like(snod),':k')
    ax.plot(dt,tice, lw=5, c='cornflowerblue', label='HIGTSI ice')

    ax.plot(dt,so,'x', markeredgewidth=4, c='royalblue', ms=8, label='Transect snow')
    ax.plot(dt,io,'x', markeredgewidth=4, c='purple', ms=8, label='Transect winter ice')
    

    ax.legend(fontsize=18,loc='lower left')

    ax.set_ylabel('Ice thickness/Snow depth (m)',fontsize=20) # Y axis data label

    ax.set_xlim(datetime(2019,9,1),datetime(2020,7,29))

    ax.tick_params(axis="x", labelsize=14)
    ax.tick_params(axis="y", labelsize=14)

    fig1.autofmt_xdate()

    fig1.savefig(outpath+'sm_season'+loc,bbox_inches='tight')
    plt.show()


