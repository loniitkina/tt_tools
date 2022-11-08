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


fig1 = plt.figure(figsize=(15,8))
ax = fig1.add_subplot(111)
ax.set_ylabel('Ocean heat flux (W/m$^2$)',fontsize=20)
ax.set_xlim(datetime(2019,10,1),datetime(2020,8,1))

all_data=[]
all_dt=[]
for fname in flist:
    buoy_name=fname.split('flux')[-1].split('.')[0]
    print(buoy_name)

    dates = getColumn(fname,0,skipheader=1, delimiter=',')
    dt = [ datetime.strptime(x, '%Y-%m-%d %H:%M:%S') for x in dates ]
    
    fo = getColumn(fname,1,skipheader=1, delimiter=',');fo = np.array(fo,dtype=np.float)
    
    #the longest time series
    if buoy_name=='2019T69':
        plt.plot(dt,np.zeros_like(fo),'--k')
        dt_long=dt

    
    mask=(np.abs(fo)>250) | ((np.abs(fo)>40) & (np.array(dt)>melt))
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
print(ts)

flux=ts.values
#ax.plot(dt_long,flux)

flux = np.ma.masked_invalid(flux)
mean = np.mean(flux,axis=1)

ax.plot(dt_long,mean,':k',lw=3, label='mean')

#get a smooth ocean heat flux - like an average surface heat flux representative or large areas
#clue: T62 anf T66 are less than 1 km apart, and show very different heat flux spikes.
#fit the curve
x = mdates.date2num(all_dt)
y = all_data
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
fig1.savefig(outpath+'ts_ocean_heat_flux_forSnowModel.png',bbox_inches='tight')

