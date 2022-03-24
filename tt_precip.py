from netCDF4 import Dataset
import numpy as np
from glob import glob
import pandas as pd
from datetime import datetime, timedelta
from tt_func import getColumn
import matplotlib.pyplot as plt

#ARM precipitation
inpath='../data/weather_ARM/'
fnames = sorted(glob(inpath+'moswbpluvio2S3.a1.*.nc'))
#file_ts='precipitation_ARM_3h.csv'

ts_time=[]
ts_precip1=[]
ts_precip2=[]
ts_track_valid=[]

for fname in fnames:
    #print(fname)
    f = Dataset(fname)
    #"Accumulated amounts of precipitation over the sampling interval exceeding a threshold of 0.05mm or the accumulated amount of fine precipitation observed over the last hour"
    #The accum_rtnrt variable is calculated by first measuring the accumulated amount of rain in the last minute. If this measurement exceeds the threshold, it reports this real time value. If the real time measurement does not reach the threshold, it reports the non real time measurement using the same equation as the accum_nrt variable.
    #units = "mm"
    sf1 = f.variables['accum_rtnrt'][:]
    
    #The accum_nrt variable is calculated by measuring the amount of rain accumulate in a sampling interval at most 1 hour long, with the end of the interval at the given time. The start of the sampling interval occurs within the past hour, but is unknown. The start of the interval is determined once the accumulated sum either exceeds 0.05 or the interval length reaches an hour
    #mainly same, ut gives much lower values during extreme events
    sf2 = f.variables['accum_nrt'][:]
    
    #time steps are randomly long intervals
    #base_time:units = "seconds since 1970-1-1 0:00:00 0:00"
    bt = f.variables['base_time'][:]
    #time_offset:units = "seconds since 2019-10-17 00:00:00 0:00"
    to = f.variables['time_offset'][:]
    time = np.array(bt+to, dtype='datetime64[s]')
    
    #track valid values (pandas assign 0 to times without values/observations gaps)
    track_valid=sf1+1000
    
    ts_time.extend(time)
    ts_precip1.extend(sf1)
    ts_precip2.extend(sf2)
    ts_track_valid.extend(track_valid)

#make time series of 3-h sums
snow = {'snowfall1': ts_precip1,
        'snowfall2': ts_precip2,
        'valid': ts_track_valid}

df1 = pd.DataFrame(data=snow,index=ts_time)

#sums = df.groupby(pd.Grouper(freq='3H')).sum()
#sums = sums.asfreq('3H')
sums1 = df1.resample('3H').sum().asfreq('3H')


#Matrosov precipitation
inpath='../data/weather_Matrosov/mosaic-snowfall/'
fnames = sorted(glob(inpath+'kazr-snow-rate-20*.dat'))
file_ts='precipitation_ARM_Matrosov_3h.csv'

ts_time3=[]
ts_precip3=[]
ts_track_valid3=[]

for fname in fnames:
    print(fname)
    
    date1=fname.split('-')[-3]
    offset=datetime.strptime(date1, '%Y%m')
    #print(offset)
    
    days = getColumn(fname,0,skipheader=0,delimiter=',')
    days = np.array(days,dtype=np.float)
    
    time = [ offset+timedelta(days=x) for x in days ]
    #print(time)
    
    #mm/hour
    pp = getColumn(fname,1,skipheader=0,delimiter=',')
    pp = np.array(pp,dtype=np.float)/120    #convert to mm/30sec
    
    valid=pp+1000
    
    ts_time3.extend(time)
    ts_precip3.extend(pp)
    ts_track_valid3.extend(valid)

#plt.plot(ts_time,ts_precip2)
#plt.plot(ts_time3,ts_precip3)
#plt.show()

#make time series of 3-h sums
snow = {'snowfall3': ts_precip3,
        'valid3': ts_track_valid3}

df2 = pd.DataFrame(data=snow,index=ts_time3)
sums2 = df2.resample('3H').sum().asfreq('3H')
sums=sums1.combine_first(sums2)
print(sums)





#keep values
snow1 = sums.snowfall1.values
snow2 = sums.snowfall2.values
snow3 = sums.snowfall3.values
valid = sums.valid.values
valid3 = sums.valid3.values
dates = sums.index.values

snow1=np.ma.array(snow1,mask=valid==0,fill_value=-9999)
snow2=np.ma.array(snow2,mask=valid==0,fill_value=-9999)
snow3=np.ma.array(snow3,mask=valid3==0,fill_value=-9999)

snow1 = np.ma.masked_invalid(snow1)
snow2 = np.ma.masked_invalid(snow2)
snow3 = np.ma.masked_invalid(snow3)

#max rates
print(np.max(snow1))
print(np.max(snow2))
print(np.max(snow3))

#cumulative snow
print(np.sum(snow1))
print(np.sum(snow2))
print(np.sum(snow3))


#plotting
#plt.plot(dates,np.cumsum(snow1,axis=0),c='b',label='accum_rtnrt')
#plt.plot(dates,np.cumsum(snow2,axis=0),c='r',label='accum_nrt')
plt.plot(dates,np.cumsum(snow3,axis=0),c='g',label='kazr')

plt.legend()
plt.show()

plt.plot(dates,snow1,c='b',label='accum_rtnrt')
plt.plot(dates,snow2,c='r',label='accum_nrt')
plt.plot(dates,snow3,c='g',label='kazr')

plt.legend()
plt.show()

#convert back to datetime list
dt = dates.astype('O')
dates = [ datetime.utcfromtimestamp(x/1e9) for x in dt ]

#prepare output for SnowModel
year = [ datetime.strftime(x, "%Y") for x in dates ]
month = [ datetime.strftime(x, "%m") for x in dates ]
day = [ datetime.strftime(x, "%d") for x in dates ]
hour = [ datetime.strftime(x, "%H") for x in dates ]

#time series text file exports
tt = [year,month,day,hour,np.round(snow1.filled(),4),np.round(snow2.filled(),4),np.round(snow3.filled(),4)]
table = list(zip(*tt))

print(inpath+file_ts)
with open(inpath+file_ts, 'wb') as f:
    #header
    f.write(b'year,month,day,hour,accum_rtnrt (ARM) (mm/3h), accum_nrt (ARM) (mm/3h), KAZR-Matrosov (mm/3h)\n')
    np.savetxt(f, table, fmt="%s", delimiter=",")

                
