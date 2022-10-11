import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from tt_func import getColumn

inpath='../data/SnowModel/seasonal_plot/'
outpath='../plots_sm/'

fname = inpath+'snod.dat'
snod = getColumn(fname,1, delimiter=',')
snod = np.array(snod,dtype=np.float)     
snod = np.ma.array(snod,mask=snod==-9999)

fname = inpath+'tice.dat'
tice = getColumn(fname,1, delimiter=',')
tice = np.array(tice,dtype=np.float)     
tice = np.ma.array(tice,mask=tice==-9999)*-1

fname = inpath+'snod_tice1_tice2_obs.dat'
so = getColumn(fname,1, delimiter=',')
so = np.array(so,dtype=np.float)     
so = np.ma.array(so,mask=so==-9999)

fname = inpath+'snod_tice1_tice2_obs.dat'
io1 = getColumn(fname,2, delimiter=',')
io1 = np.array(io1,dtype=np.float)     
io1 = np.ma.array(io1,mask=io1==-9999)*-1

fname = inpath+'snod_tice1_tice2_obs.dat'
io2 = getColumn(fname,3, delimiter=',')
io2 = np.array(io2,dtype=np.float)     
io2 = np.ma.array(io2,mask=io2==-9999)*-1

numdays=365
start = datetime(2019,8,1)
dt = [start + timedelta(days=x) for x in range(numdays)]

fig1 = plt.figure(figsize=(10,10))
ax = fig1.add_subplot(111)

ax.plot(dt,snod, lw=5, c='turquoise', label='SnowModel snow')
ax.plot(dt,np.zeros_like(snod),':k')
ax.plot(dt,tice, lw=5, c='cornflowerblue', label='SnowModel ice (HIGTSI)')

ax.plot(dt,so,'x', markeredgewidth=4, c='royalblue', ms=8, label='Transect snow')
ax.plot(dt,io1,'x', markeredgewidth=4, c='purple', ms=8, label='Transect winter ice')
ax.plot(dt,io2,'x', markeredgewidth=4, c= 'orange', ms=8, label='Transect summer ice')

ax.legend(fontsize=20,loc='lower left')

ax.set_ylabel('Ice thickness/Snow depth (m)',fontsize=20) # Y axis data label

ax.set_xlim(datetime(2019,9,1),datetime(2020,7,29))

ax.tick_params(axis="x", labelsize=14)
ax.tick_params(axis="y", labelsize=14)

fig1.autofmt_xdate()

fig1.savefig(outpath+'sm_season',bbox_inches='tight')
plt.show()


