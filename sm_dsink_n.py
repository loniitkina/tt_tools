import csv
import re
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from tt_func import getColumn
import pandas as pd

#TO DO: add precipitation rate
#TO DO: compare to snow mass balance terms in SnowModel
#TO DO: add all ice age locations: Nloop, Sloop, Runway

#whenever there is strong deformation, strong wind and no large precipitation we have an increase
#if strong deformation, but also precipitation, we get a net increase

loc = 'Nloop'

#set up plot
fig1 = plt.figure(figsize=(10,10))
ax = fig1.add_subplot(111)

#observations
inpath_table = '../data/MCS/MP/'
fname = inpath_table+'ts_'+loc+'_1m_gridded_swe.csv'    #all obs
fname = inpath_table+'ts_'+loc+'_1m_gridded_swe_period.csv'    #end of deformation periods

obs_swe = getColumn(fname,9); obs_swe = np.array(obs_swe,dtype=np.float)

year = np.array(getColumn(fname,0),dtype=int)
month = np.array(getColumn(fname,1),dtype=int)
day = np.array(getColumn(fname,2),dtype=int)
obs_dates = [ datetime(year[x],month[x],day[x]) for x in range(0,len(year)) ] 

ax.plot(obs_dates,obs_swe,'x', markeredgewidth=4, c='royalblue', ms=8, label='Transect snow')


##simulations
#inpath='../data/SnowModel/'
#outpath='../plots_sm/'

#fname = inpath+'swed_'+loc+'.dat'
#swed = getColumn(fname,2, delimiter=',')
#swed = np.array(swed,dtype=np.float)     
#swed = np.ma.array(swed,mask=swed==-9999)

#numdays=365*8
#start = datetime(2019,8,1)
#dt = [start + timedelta(hours=x*3) for x in range(numdays)]

#ax.plot(dt,swed[7:], lw=1, c='r', label='SnowModel snow wrong time axis')





#inpath='../data/g/'
#outpath='../plots_sm/'

#fname = inpath+'swed_'+loc+'.dat'
#swed = getColumn(fname,2, delimiter=',')
#swed = np.array(swed,dtype=np.float) 
#swed = np.ma.array(swed,mask=swed==-9999)

#numdays=366*8
#start = datetime(2019,8,1)
#dt = [start + timedelta(hours=x*3) for x in range(numdays)]

#swed = np.append([0],swed)
#ax.plot(dt,swed, lw=3, c='k', label='SnowModel snow')
#ax.plot(dt,np.zeros_like(swed),':k')

#ax.plot(dt,swed, lw=1, c='k', label='old SnowModel snow')


inpath='../data/SnowModel/final/'
outpath='../plots_sm/'

fname = inpath+'swed_'+loc+'.dat'
fname = inpath+'snow_tice_'+loc+'_2023_02_14.dat'
#iter,swed_mod1,swed_mod2,snod,sden,dyn_corr,tice,swed_obs,sden_obs,snod_obs,timo_obs

results = csv.reader(open(fname))
#get rid of all multi-white spaces and split in those that remain
results_clean = [re.sub(" +", " ",row[0]) for row in results]

swed = [row.split(" ")[2] for row in results_clean]
swed = np.array(swed,dtype=np.float)     
swed = np.ma.array(swed,mask=swed==-9999)

ds = [row.split(" ")[6] for row in results_clean]
ds = np.array(ds,dtype=np.float)     
ds = np.ma.array(ds,mask=ds==-9999)


#swed = getColumn(fname,2, delimiter=',')
#swed = np.array(swed,dtype=np.float)     
#swed = np.ma.array(swed,mask=swed==-9999)

numdays=366*8
start = datetime(2019,8,1)
dt = [start + timedelta(hours=x*3) for x in range(numdays)]
end = datetime(2020,8,1)



ax.plot(dt,swed, lw=3, c='k', label='SnowModel snow')
#ax.plot(dt,ds, c='k', label='SnowModel d-sink')
#ax.plot(dt,np.cumsum(ds), c='g', label='SnowModel d-sink cumsum')
ax.plot(dt,np.zeros_like(swed),':k')


#get wind speed
inpath='../data/SnowModel/'

fname = inpath+'final_10m_3hrly_met_forcing.dat'
#print(fname)

results = csv.reader(open(fname))
#get rid of all multi-white spaces and split in those that remain
results_clean = [re.sub(" +", " ",row[0]) for row in results]

#temperature, humidity, wind speed, wind direction, precipitation
ws = [row.split(" ")[4] for row in results_clean]
ws = np.array(ws,dtype=np.float)     
ws = np.ma.array(ws,mask=ws==-9999)

##plot wind speed
#ax.plot(dt,ws[8:],label='wind speed')

#get deformation
inpath = '../data/mosaic_buoy_data/selection/'
fname = inpath+'Deformation_3hr.csv'

td = getColumn(fname,7); td = np.array(td,dtype=np.float)

year = np.array(getColumn(fname,0),dtype=int)
month = np.array(getColumn(fname,1),dtype=int)
day = np.array(getColumn(fname,2),dtype=int)
#td_dates = [ datetime(year[x],month[x],day[x]) for x in range(0,len(year)) ]
#include 3-hour time lag for deformation (buoys show deformation for past hour)
td_dates = [ datetime(year[x],month[x],day[x])+ timedelta(hours=3) for x in range(0,len(year)) ] 

##plot deformation
#ax.plot(td_dates,td,label='total deformation')

#precipitation
inpath='../data/weather_Matrosov/mosaic-snowfall/'
fname=inpath+'precipitation_ARM_Matrosov_3h.csv'

#take only the start, we dont need summer data
pp = getColumn(fname,6)[:-400]; pp = np.array(pp,dtype=np.float)
pp = np.cumsum(np.ma.array(pp,mask=pp==-9999.0))*3/1000  #from mm/3hr to m

year = np.array(getColumn(fname,0),dtype=int)[:-400]
month = np.array(getColumn(fname,1),dtype=int)[:-400]
day = np.array(getColumn(fname,2),dtype=int)[:-400]
pp_dates = [ datetime(year[x],month[x],day[x]) for x in range(0,len(year)) ]

#ax.plot(pp_dates,pp,label='precip')

#get all data on the same time scale
#add dummy obs to start and end of the model simulation time series
obs_swe = np.append([0], obs_swe)
obs_swe = np.append(obs_swe, [0])
obs_dates = np.append([dt[0]], obs_dates)
obs_dates = np.append(obs_dates,[dt[-1]])

#resample observations to 3-H steps
pos = {'swe': obs_swe}
df = pd.DataFrame(data=pos,index=obs_dates)
sums = df.resample('3H').sum().asfreq('3H')
obs_swe3h = sums.swe.values

#calculate D-sink
d_sink = swed - obs_swe3h
#d_sink = obs_swe3h
mask=obs_swe3h==0
d_sink=np.where(mask,0,d_sink)

#ax.plot(dt,np.ma.array(d_sink,mask=mask),'X',ms=8, c='r', label='model-obs')

td = np.append([0], td)
td = np.append(td, [0])
td_dates = np.append([dt[0]], td_dates)
td_dates = np.append(td_dates,[dt[-1]])

#resample observations to 3-H steps
pos = {'td': td}
df = pd.DataFrame(data=pos,index=td_dates)
sums = df.resample('3H').sum().asfreq('3H')
td3h = sums.td.values

#same for precip
pos = {'td': td}
df = pd.DataFrame(data=pos,index=td_dates)
sums = df.resample('3H').sum().asfreq('3H')
td3h = sums.td.values

pp = np.append([0], pp)
pp = np.append(pp, [0])
pp_dates = np.append([dt[0]], pp_dates)
pp_dates = np.append(pp_dates,[dt[-1]])

pos = {'pp': pp}
df = pd.DataFrame(data=pos,index=pp_dates)
sums = df.resample('3H').sum().asfreq('3H')
pp3h = sums.pp.values

#make cumulative variables also for wind and for deformation

#get only wind above 5 m/s (blowing snow)
wind5 = np.ma.array(ws,mask=ws<5)
#wind5_b = np.where(wind>5,1,0)
wind5_cum = np.cumsum(wind5)

td3h_cum = np.cumsum(td3h)

#ax.plot(dt,wind5_cum[8:],label='cum wind speed')
#ax.plot(dt,pp3h_cum,label='cum precip')

#insert zeros
wind5_cum0 = np.where(mask,0,wind5_cum)
td3h_cum0 = np.where(mask,0,td3h_cum)
pp3h0 = np.where(mask,0,pp3h)
swed0 = np.where(mask,0,swed)

#make one common timeseries
pos = {'td': td3h_cum0,
       'pp': pp3h0,
       'wind': wind5_cum0,
       'sink': d_sink,
       'swed':swed0}
df = pd.DataFrame(data=pos,index=dt)

#replace zeros by next value at observation
df = df.replace(to_replace=0, method='ffill')

wc = df.wind.values
dc = df.td.values
sc = df.sink.values
fc = df.swed.values
pc = df.pp.values

#ax.plot(dt,sc,'o', c='g', label='SWE sink')

#get rate of change between observation steps
dwc = wc[:-1]-wc[1:]
ddc = dc[:-1]-dc[1:]
dsc = sc[:-1]-sc[1:]
dfc = fc[:-1]-fc[1:]
dpc = pc[:-1]-pc[1:]

##mask again all values between observations by zeros
#dwc = np.ma.array(dwc,mask=mask[:-1])
#ddc = np.ma.array(ddc,mask=mask[:-1])
#dsc = np.ma.array(dsc,mask=mask[:-1])
#dfc = np.ma.array(dfc,mask=mask[:-1])
#dpc = np.ma.array(dpc,mask=mask[:-1])

dwc = np.ma.array(dwc,mask=mask[1:])
ddc = np.ma.array(ddc,mask=mask[1:])
dsc = np.ma.array(dsc,mask=mask[1:])
dfc = np.ma.array(dfc,mask=mask[1:])
dpc = np.ma.array(dpc,mask=mask[1:])

dsc_m = dsc.compressed()
ddc_m = ddc.compressed()
dwc_m = dwc.compressed()
dfc_m = dfc.compressed()
dpc_m = dpc.compressed()
dt_m = np.ma.array(dt[:],mask=mask).compressed()

#dsc_m = np.append([0],dsc_m[:-1])

#all sinks
mask = (dsc_m > 0.1)
#only large sinks and large deformation
#mask = (ddc_m/100 > -.021) | (np.abs(dsc_m) < 0.002)


dsc_m = np.ma.array(dsc_m, mask=mask).compressed()
ddc_m = np.ma.array(ddc_m, mask=mask).compressed()
dwc_m = np.ma.array(dwc_m, mask=mask).compressed()
dfc_m = np.ma.array(dfc_m, mask=mask).compressed()
dpc_m = np.ma.array(dpc_m, mask=mask).compressed()

dt_m = np.ma.array(dt_m, mask=mask).compressed()

#scale some values
ax.plot(dt_m,dsc_m,'x', markeredgewidth=6, c='gold', ms=8, label=r'$\frac{dD}{dt}$')
#ax.plot(dt[1:],dwc/20000,'x', markeredgewidth=4, c='r', ms=8, label='dt cum wind > 5m/s')
ax.plot(dt,td3h_cum/1000, c='purple', label=r'$\sum_{i=1}^k \epsilon_{total}$')
#ax.plot(dt,d_sink, c='gold', label='residual')
ax.plot(dt_m,ddc_m/100,'x', markeredgewidth=3, c='purple', ms=8, label=r'$\frac{d\sum_{i=1}^k \epsilon_{total}}{dt}$')
ax.plot(dt,dc/100,'x', markeredgewidth=3, c='purple', ms=1, label='test')
#ax.plot(dt[1:],dfc,'x', markeredgewidth=4, c='b', ms=8, label='dt cum swe')
#ax.plot(dt[1:],dpc,'x', markeredgewidth=4, c='g', ms=8, label='dt cum swe precip')

#finalize the plot
ax.legend(fontsize=18,loc='upper left',ncol=2)

ax.set_ylabel('SWE (m)',fontsize=20) # Y axis data label

ax.set_xlim(datetime(2019,8,1),datetime(2020,7,31))
#ax.set_ylim(-.05,.2)
#ax.set_ylim(-.1,.2)

ax.tick_params(axis="x", labelsize=14)
ax.tick_params(axis="y", labelsize=14)

plt.grid()

fig1.autofmt_xdate()

plt.show()
fig1.savefig(outpath+'sm_dsink_2',bbox_inches='tight')


#start the scatter plot
fig2 = plt.figure(figsize=(10,10))
bx = fig2.add_subplot(111)

bx.plot(np.abs(dsc_m),ddc_m/100,'X', markeredgewidth=3, ms=15, mec='purple', c='gold')
#bx.plot(dsc_m,dwc_m/10000,'o', label='wind >5m/s')

##binary wind
#bw = np.where(dwc_m/10000<-.005,1,0)
#bw_mark = (ddc_m/100)*bw

#bx.plot(dsc_m,bw_mark,'x',c='r')

##binary snowfall
#bp = np.where(dpc_m<-.1,1,0)
#bp_mark = (ddc_m/100)*bp

#bx.plot(dsc_m,bp_mark,'x',c='b')

#fit the curve
#r2 estimates
x = np.abs(dsc_m)[1:]   #exclude the first one, not a real deformation period (several periods)
y = (ddc_m/100)[1:]
model = np.polyfit(x, y, 1)
print('coefficients: ', model)

predict = np.poly1d(model)
from sklearn.metrics import r2_score
r2 = r2_score(y, predict(x))
print('R2: ',r2)

x_lin_reg = np.arange(0, .01,.001)
y_lin_reg = predict(x_lin_reg)

print(x_lin_reg)
print(y_lin_reg)

bx.plot(x_lin_reg, y_lin_reg, c='r')#, label=datel[dd])

#cx[2].scatter(dt,r2,facecolors=colors[dd],s=70)

#get siginificance
from scipy.stats import linregress
print(linregress(x,y))
slope,intercept,rvalue,pvalue,stderr=linregress(x,y)
#p-value : two-sided p-value for a hypothesis test whose null hypothesis is that the slope is zero
if pvalue < 0.0001:
    #cx[2].scatter(dt,r2,marker='x',c='k',s=70)
    print('significant!')

bx.text(0, -.02, '$R^2$= '+str(np.round(r2,2)), ha="left", va="center", size=20)
bx.text(0, -.025, '$N$= '+str(np.round(len(x),2)), ha="left", va="center", size=20)


bx.set_xlabel(r'$\frac{dD}{dt}$',fontsize=20)
bx.set_ylabel(r'$\frac{d\sum_{i=1}^k \epsilon_{total}}{dt}$',fontsize=20)
#bx.legend()
plt.show()
fig2.savefig(outpath+'sm_dsink_scatter_2'+loc,bbox_inches='tight')


#we lumped all errors in atm forcing, in observations and in model AND deformation into this residual D-term
#if we can show that deformation is the prevailing signal in D-term then our assumption that all those errors are small is correct!!!

#this study is only possible because:
#atmospheric forcing is local and very good
#sea ice deformation at appropriate temporal scale (not SAR)
#our observations are frequnet enough - at synoptic time scale - one sampling between every storm!!!

#future work: 
#sensitivitiy studies of snow thermal conductivity, snow sublimation etc.
#replace sea ice deformation from buoys by ship radar
#do a 3D simulation
