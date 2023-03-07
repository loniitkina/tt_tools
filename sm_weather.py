import csv
import re
import numpy as np
import matplotlib.pyplot as plt
from tt_func import getColumn
from datetime import datetime, timedelta

inpath='../data/SnowModel/'
inpath='../data/SnowModel/final/'
outpath='../plots_sm/'

fname = inpath+'final_10m_3hrly_met_forcing.dat'
fname = inpath+'final_10m_3hrly_met_2023_02_14.dat'
print(fname)

results = csv.reader(open(fname))
#get rid of all multi-white spaces and split in those that remain
results_clean = [re.sub(" +", " ",row[0]) for row in results]

#temperature, humidity, wind speed, wind direction, precipitation

tair = [row.split(" ")[2] for row in results_clean]
tair = np.array(tair,dtype=np.float)     
tair = np.ma.array(tair,mask=tair==-9999)

tair_model = [row.split(" ")[3] for row in results_clean]
tair_model = np.array(tair_model,dtype=np.float)     
tair_model = np.ma.array(tair_model,mask=tair_model==-9999)

rh = [row.split(" ")[4] for row in results_clean]
rh = np.array(rh,dtype=np.float)     
rh = np.ma.array(rh,mask=rh==-9999)

rh_model = [row.split(" ")[5] for row in results_clean]
rh_model = np.array(rh_model,dtype=np.float)     
rh_model = np.ma.array(rh_model,mask=rh==-9999)

ws = [row.split(" ")[6] for row in results_clean]
ws = np.array(ws,dtype=np.float)     
ws = np.ma.array(ws,mask=ws==-9999)

ws_model = [row.split(" ")[7] for row in results_clean]
ws_model = np.array(ws_model,dtype=np.float)     
ws_model = np.ma.array(ws_model,mask=ws==-9999)

wd = [row.split(" ")[8] for row in results_clean]
wd = np.array(wd,dtype=np.float)     
wd = np.ma.array(wd,mask=wd==-9999)

wd_model = [row.split(" ")[9] for row in results_clean]
wd_model = np.array(wd_model,dtype=np.float)     
wd_model = np.ma.array(wd_model,mask=wd==-9999)

pp = [row.split(" ")[10] for row in results_clean]
pp = np.array(pp,dtype=np.float)     
pp = np.ma.array(pp,mask=pp==-9999)/10  #match Glen's plot #WARNING - please chck if this is OK!

pp_model = [row.split(" ")[11] for row in results_clean]
pp_model = np.array(pp_model,dtype=np.float)     
pp_model = np.ma.array(pp_model,mask=pp==-9999)/10

pp_cum = np.cumsum(pp_model/1000)    #convert to meters

##import also indexes to tell apart measured and reanalysis data
#inpath='../data/SnowModel/'
#fname = inpath+'index_10m_3hrly_met.dat'
#print(fname)

#results = csv.reader(open(fname))
##get rid of all multi-white spaces and split in those that remain
#results_clean = [re.sub(" +", " ",row[0]) for row in results]

##1=reanalysis model, 2=observations
#idx_tair = [row.split(" ")[2] for row in results_clean]
#idx_tair = np.array(idx_tair,dtype=np.float)
#idx_tair = np.where(idx_tair==1,1,0)
##tair_model = np.ma.array(tair,mask=idx_tair)

#idx_rh = [row.split(" ")[3] for row in results_clean]
#idx_rh = np.array(idx_rh,dtype=np.float)
#idx_rh = np.where(idx_rh==1,1,0)
#rh_model = np.ma.array(rh,mask=idx_rh)

#idx_ws = [row.split(" ")[4] for row in results_clean]
#idx_ws = np.array(idx_ws,dtype=np.float)
#idx_ws = np.where(idx_ws==1,1,0)
#ws_model = np.ma.array(ws,mask=idx_ws)

#idx_pp = [row.split(" ")[6] for row in results_clean]
#idx_pp = np.array(idx_pp,dtype=np.float)
#idx_pp = np.where(idx_pp==1,1,0)
#pp_model = np.ma.array(pp,mask=idx_pp)
#pp_cum_model = np.ma.array(pp_cum,mask=idx_pp)

#dates
numdays=366*8
start = datetime(2019,8,1)
dt = [start + timedelta(hours=x*3) for x in range(numdays)]
end = datetime(2020,8,1)

#ocean heat fluxes
inpath = '../data/IMB_Lei_PANGAEA/'
fname = inpath+'ocean_heat_flux_for_HIGTSI_new.csv'

fo = getColumn(fname,4); fo = np.array(fo,dtype=np.float)
fo = np.ma.array(fo,mask=fo==-9999)

year = np.array(getColumn(fname,0),dtype=int)
month = np.array(getColumn(fname,1),dtype=int)
day = np.array(getColumn(fname,2),dtype=int)
hour = np.array(getColumn(fname,3),dtype=int)
fo_dt = [ datetime(year[x],month[x],day[x],hour[x]) for x in range(0,len(year)) ]

#Plotting the time series
fig1, ax = plt.subplots(5, 1,gridspec_kw={'height_ratios': [1,.5,.5,1,.3]},figsize=(10,15))

#air temperature
ax[0].set_ylabel('T$_{air}$ ($^\circ$C)', fontsize=15)
ax[0].tick_params(axis="x", labelsize=12)
ax[0].tick_params(axis="y", labelsize=12)
ax[0].set_xlim(start,end)

ax[0].plot(dt,tair_model,c='k')
ax[0].plot(dt,tair,c='darkred')
zeros=np.zeros_like(tair_model)
ax[0].plot(dt,zeros,c='k')

#relative humidity
ax[1].set_ylabel('$\Phi_{air}$ (%)', fontsize=15)
ax[1].tick_params(axis="x", labelsize=12)
ax[1].tick_params(axis="y", labelsize=12)
ax[1].set_xlim(start,end)

ax[1].plot(dt,rh_model,c='k')
ax[1].plot(dt,rh,c='teal')

#precipitation
ax[2].set_ylabel('Precipitation (mm/3h)', fontsize=15)
ax[2].tick_params(axis="x", labelsize=12)
ax[2].tick_params(axis="y", labelsize=12)
ax[2].set_xlim(start,end)

ax[2].plot(dt,pp_model,'*',c='k')
ax[2].plot(dt,pp,'*',c='royalblue')

ax1 = ax[2].twinx()
ax1.set_ylabel('Cum. Precipitation (m)', fontsize=15)
ax1.plot(dt,pp_cum,c='b')
#ax1.plot(dt,pp_cum_model,c='k')

#wind speed and direction
ax[3].set_ylabel('Wind Speed (m/s)', fontsize=15)
ax[3].tick_params(axis="x", labelsize=12)
ax[3].tick_params(axis="y", labelsize=12)
ax[3].set_xlim(start,end)

cs = ax[3].scatter(dt,ws_model,c='k',s=3)
cs = ax[3].scatter(dt,ws,c=wd,cmap=plt.cm.twilight)
cb = plt.colorbar(cs,orientation='horizontal',aspect=80, fraction=.05, pad=.2)  # draw colorbar
cb.set_label(label='Wind direction (deg.)',fontsize=15)

#horizontal line for drifting snow limit (7.7m/s based on dry snow estimate of Li and Pomeroy, 1997)
driftsnow=np.ones_like(ws_model)*7.7
ax[3].plot(dt,driftsnow,c='k')

ax[4].set_ylabel('F$_{ocean}$ (W/m$^2$)', fontsize=15)
ax[4].tick_params(axis="x", labelsize=12)
ax[4].tick_params(axis="y", labelsize=12)
ax[4].set_xlim(start,end)

ax[4].plot(fo_dt,fo,c='royalblue')

#dates for the publisher
from matplotlib.dates import MonthLocator, DateFormatter
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

ax[0].xaxis.set_minor_locator(MonthLocator())
ax[0].xaxis.set_major_formatter(DateFormatter('%b %Y'))

ax[1].xaxis.set_minor_locator(MonthLocator())
ax[1].xaxis.set_major_formatter(DateFormatter('%b %Y'))

ax[2].xaxis.set_minor_locator(MonthLocator())
ax[2].xaxis.set_major_formatter(DateFormatter('%b %Y'))

ax[3].xaxis.set_minor_locator(MonthLocator())
ax[3].xaxis.set_major_formatter(DateFormatter('%b %Y'))

#plt.show()
fig1.savefig(outpath+'sm_weather.png',bbox_inches='tight')
