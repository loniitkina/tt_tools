import csv
import re
import numpy as np
import matplotlib.pyplot as plt
from tt_func import getColumn
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
pp = np.ma.array(pp,mask=pp==-9999)

pp_model = [row.split(" ")[11] for row in results_clean]
pp_model = np.array(pp_model,dtype=np.float)     
pp_model = np.ma.array(pp_model,mask=pp==-9999)

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

##get also precipitation directly from input to compare the double-check the units
#inpath='../data/weather_Matrosov/mosaic-snowfall/'
#fname=inpath+'precipitation_ARM_Matrosov_3h.csv'

#po = getColumn(fname,6); po = np.array(po,dtype=np.float)
#po = np.ma.array(po,mask=po==-9999)

#year = np.array(getColumn(fname,0),dtype=int)
#month = np.array(getColumn(fname,1),dtype=int)
#day = np.array(getColumn(fname,2),dtype=int)
#hour = np.array(getColumn(fname,3),dtype=int)
#po_dt = [ datetime(year[x],month[x],day[x],hour[x]) for x in range(0,len(year)) ]

#ocean heat fluxes
inpath = '../data/IMB_Lei_PANGAEA/'
fname = inpath+'ocean_heat_flux_for_HIGTSI_LS.csv'

fo = getColumn(fname,4); fo = np.array(fo,dtype=np.float)
fo = np.ma.array(fo,mask=fo==-9999)

year = np.array(getColumn(fname,0),dtype=int)
month = np.array(getColumn(fname,1),dtype=int)
day = np.array(getColumn(fname,2),dtype=int)
hour = np.array(getColumn(fname,3),dtype=int)
fo_dt = [ datetime(year[x],month[x],day[x],hour[x]) for x in range(0,len(year)) ]

#deformation
inpath_buoys = '../data/mosaic_buoy_data/selection/'
fname = inpath_buoys+'Deformation_3hr.csv'

#total deformation
td = getColumn(fname,7); td = np.array(td,dtype=np.float)

year = np.array(getColumn(fname,0),dtype=int)
month = np.array(getColumn(fname,1),dtype=int)
day = np.array(getColumn(fname,2),dtype=int)
#td_dates = [ datetime(year[x],month[x],day[x]) for x in range(0,len(year)) ]
#include 3-hour time lag for deformation (buoys show deformation for past hour)
td_dt = [ datetime(year[x],month[x],day[x])+ timedelta(hours=3) for x in range(0,len(year)) ] 

#Plotting the time series
fig1 = plt.figure(figsize=(10,5))
ax = fig1.add_subplot(111)

#wind speed and direction
start = datetime(2020,3,16)
end = datetime(2020,3,27)
ax.set_ylabel('Wind Speed (m/s)', fontsize=10)
ax.tick_params(axis="x", labelsize=10)
ax.tick_params(axis="y", labelsize=10)
ax.set_xlim(start,end)

cs = ax.scatter(dt,ws_model,c='k',s=3)
cs = ax.scatter(dt,ws,c=wd,cmap=plt.cm.rainbow)
cb = plt.colorbar(cs,orientation='horizontal',aspect=100, fraction=.3, pad=.2)  # draw colorbar
cb.set_label(label='Wind dir. (deg.)', fontsize=10)

#horizontal line for drifting snow limit (7.7m/s based on dry snow estimate of Li and Pomeroy, 1997)
driftsnow=np.ones_like(ws_model)*7.7
ax.plot(dt,driftsnow,c='k')



#dates for the publisher
from matplotlib.dates import MonthLocator, DateFormatter
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')



ax.xaxis.set_minor_locator(MonthLocator())
ax.xaxis.set_major_formatter(DateFormatter('%d %b'))


plt.show()
fig1.savefig(outpath+'sid_weather.png',bbox_inches='tight')
