import csv
import re
import numpy as np
import matplotlib.pyplot as plt
from tt_func import getColumn, running_stats
from datetime import datetime, timedelta

#a script to plot all the forcing: weather and sea ice deformation

inpath='../data/SnowModel/final/'
outpath='../plots_sm/'

fname = inpath+'final_10m_3hrly_met_2023_02_14.dat'
print(fname)

results = csv.reader(open(fname))
#get rid of all multi-white spaces and split in those that remain
results_clean = [re.sub(" +", " ",row[0]) for row in results]

#temperature, humidity, wind speed, wind direction, precipitation
tair_model = [row.split(" ")[3] for row in results_clean]
tair_model = np.array(tair_model,dtype=np.float)     
tair_model = np.ma.array(tair_model,mask=tair_model==-9999)

tair_mean,vvv = running_stats(tair_model,3*8)  #3 days, 3 hourly (8 records per day)

#dates
numdays=366*8
start = datetime(2019,8,1)
dt = [start + timedelta(hours=x*3) for x in range(numdays)]
end = datetime(2020,8,1)
end2 = datetime(2019,9,1)

#Plotting the time series
fig1 = plt.figure(figsize=(10,8))
ax = fig1.add_subplot(111)

#air temperature
ax.set_ylabel('T$_{air}$ ($^\circ$C)', fontsize=20)
ax.tick_params(axis="x", labelsize=16)
ax.tick_params(axis="y", labelsize=16)

ax.set_xlim(start,end2)
ax.set_ylim(-5,1)

ax.plot(dt,tair_model,c='k',lw=3,label='10 m T$_{air}$')
ax.plot(dt[16:],tair_mean[16:],c='royalblue',lw=3,label='3-day running mean')


#thresholds
ones=np.ones_like(tair_model)
ax.plot(dt,ones*0,c='k',lw=2)
ax.plot(dt,ones*-.2,c='0.5',ls='--')
ax.plot(dt,ones*-1.9,c='purple',ls='--',lw=2)

#events:
ax.axvspan(datetime(2019,8,18), datetime(2019,8,19),color='royalblue',alpha=.2)    #Nloop snow accumulation onset
ax.axvspan(datetime(2019,8,30), datetime(2019,8,31),color='purple',alpha=.2)         #Sloop snow accumulation onset

ax.legend(fontsize=20, frameon=False)

#dates for the publisher
from matplotlib.dates import DayLocator, DateFormatter, WeekdayLocator, SU
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

ax.xaxis.set_minor_locator(DayLocator())
ax.xaxis.set_major_locator(WeekdayLocator(byweekday=SU, interval=1))
ax.xaxis.set_major_formatter(DateFormatter('%d %b'))

ax.tick_params(axis="x", labelsize=18)
ax.tick_params(axis="y", labelsize=18)

plt.show()
fig1.savefig(outpath+'sm_tair.png',bbox_inches='tight')
