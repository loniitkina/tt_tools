import numpy as np
from glob import glob
from datetime import datetime
import pandas as pd
from tt_func import getColumn
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from matplotlib.dates import MonthLocator, DateFormatter
import locale

inpath = '../data/IMB_Lei_PANGAEA/'
outpath='../plots_sm/'

melt=datetime(2020,6,1)

flist=sorted(glob(inpath+'Heat_flux*'+'.csv'))

#Salganik et al. (2023) estimated an ocean heat flux increase from 16 to 44 W m−2 from July 9 to July 29 
#using level ice temperatures and bottom melt rates in the Central Observatory.

fig1 = plt.figure(figsize=(15,8))
ax = fig1.add_subplot(111)
ax.set_ylabel('Ocean heat flux (W/m$^2$)',fontsize=20)
#ax.set_xlim(datetime(2019,10,1),datetime(2020,8,1))

all_data=[]
all_dt=[]
for fname in flist:
    buoy_name=fname.split('flux')[-1].split('.')[0]
    print(buoy_name)

    dates = getColumn(fname,0,skipheader=1, delimiter=',')
    dt = [ datetime.strptime(x, '%Y-%m-%d %H:%M:%S') for x in dates ]
    
    fo = getColumn(fname,1,skipheader=1, delimiter=',');fo = np.array(fo,dtype=np.float)
    
    #the longest time series
    #if buoy_name=='0approx':
    if buoy_name=='1approx':   
        plt.plot(dt,np.zeros_like(fo),'--k')
        dt_long=dt

    
    mask=(np.abs(fo)>250) | ((np.abs(fo)>45) & (np.array(dt)>melt))
    dtm=np.ma.array(dt,mask=mask).compressed()
    fom=np.ma.array(fo,mask=mask).compressed()
    
    ax.plot(dtm,fom,label=buoy_name)
    
    
    #time series
    if fname==flist[0]:
        ts = pd.Series(fom, name=buoy_name, index=dtm)
        
    else:
        ttmp = pd.Series(fom, name=buoy_name, index=dtm)
         
        ts = pd.concat([ts, ttmp], axis=1)
        ts = ts.reindex(ts.index, method='bfill')
        ts = ts.interpolate()   #get rid of nans

    #for statistical model
    all_data.extend(fom)
    all_dt.extend(dtm)

#get mean ocean heat flux
ts = ts.reindex(dt_long, method='bfill')
ts = ts.interpolate()   #get rid of nans

#get on 3h time scale (for the model)
ts3h = ts.resample('3H').sum().asfreq('3H')
#replace zeros by next value at observation
#ts3h = ts3h.replace(to_replace=0, method='bfill')
ts3h = ts3h.replace(0, np.nan)
print(ts3h)

ts3h = ts3h.interpolate()

print(ts3h)

dates = ts3h.index.values
#convert back to datetime list
dates = dates.astype('O')
dates = [ datetime.utcfromtimestamp(x/1e9) for x in dates ]


flux=ts3h.values
#ax.plot(dt_long,flux)

flux = np.ma.masked_invalid(flux)
mean = np.mean(flux,axis=1)

#get only means from the buoys that dont give unrealistic heat fluxes (-100 W/m2 and alike) - those are likely very localized...
#unrealistic are: 2019T62   2019T66   2019T69
#places: 2, 4, 6
idx = np.array([2, 4, 6])
m = np.zeros_like(flux)
m[:,idx] = 1
mean_best = np.mean(np.ma.masked_array(flux, m),axis=1)

#keep all buoys but cap all heat fluxes at 20 W/m2
mean_max20 = np.mean(np.ma.masked_array(flux, flux>20),axis=1)

#only aprox. values
flux_approx = flux[:,0]
flux_approx = flux[:,1]

#this is a rigid toping and produces abrupt jumps, smoothing needs to be used
#smoothing
from scipy.signal import savgol_filter
polyorder=3
window=31
mean_max20 = savgol_filter(mean_max20, window, polyorder)


ax.plot(dates,mean,':k',lw=3, label='mean')
ax.plot(dates,mean_best,'--k',lw=2, label='mean best')
ax.plot(dates,mean_max20,'-k',lw=2, label='mean max 20W/m2')
#ax.plot(dt_long,mean,':k',lw=3, label='mean')

#get a smooth ocean heat flux - like an average surface heat flux representative or large areas
#clue: T62 anf T66 are less than 1 km apart, and show very different heat flux spikes.
#fit the curve
x = mdates.date2num(dates)
y = mean_best
model = np.polyfit(x, y, 2) #decide here the curve-order
predict = np.poly1d(model)

xmodel = np.arange(min(x),max(x),1) #convert numbers to dates for plotting
dd = mdates.num2date(xmodel)
ymodel = predict(xmodel)

ax.plot(dd, ymodel,'--',c='0.5',lw=3,label='model')

ax.legend(ncol=2,fontsize=14)

ax.tick_params(axis="x", labelsize=14)
ax.tick_params(axis="y", labelsize=14)

#nicer dates
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
ax.xaxis.set_minor_locator(MonthLocator())
ax.xaxis.set_major_formatter(DateFormatter('%b %Y'))

plt.show()
#fig1.savefig(outpath+'ts_ocean_heat_flux_forSnowModel_new.png',bbox_inches='tight')
fig1.savefig(outpath+'ts_ocean_heat_flux_forSnowModel_LS.png',bbox_inches='tight')

#save the data for SnowModel/HIGTSI
year = [ datetime.strftime(x, "%Y") for x in dates ]
month = [ datetime.strftime(x, "%m") for x in dates ]
day = [ datetime.strftime(x, "%d") for x in dates ]
hour = [ datetime.strftime(x, "%H") for x in dates ]

#save the data in file
#file_name = inpath+'ocean_heat_flux_for_HIGTSI_new.csv'
file_name = inpath+'ocean_heat_flux_for_HIGTSI_LS.csv'
print(file_name)

tt = [year,month,day,hour,flux_approx] #negative means downwards (from atmosphere to ocean)
table = list(zip(*tt))

with open(file_name, 'wb') as f:
    #header
    #f.write(b'year,month,day,hour, approximation from Lei et al 2021 (W/m2)\n')
    f.write(b'year,month,day,hour, approximation from Lei/Salganik (W/m2)\n')
    np.savetxt(f, table, fmt="%s", delimiter=",")



