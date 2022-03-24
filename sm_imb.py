from glob import glob
from datetime import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from tt_func import getColumn

#T66=FYI coring site
#T62=SYI coring site

#load buoy temperature data
inpath = '../data/mosaic_buoy_data/original/'
fname = glob(inpath+'2019T66*_TEMP_proc.csv')[0]
print(fname)

time = getColumn(fname,0)
dt_temp = [ datetime.strptime(time[x], "%Y-%m-%dT%H:%M:%S") for x in range(len(time)) ]

#prepare an empty array for the temperature data
nt=240
tdata = np.zeros((len(dt_temp),nt))
print(tdata.shape)

for i in range(3,3+nt):
    t = getColumn(fname,i)
    t = np.array(t,dtype=float)
    tdata[:,i-3] = t

#load buoy snow depth and sea ice thickness data retreived by Lei et al (PANGAEA)
inpath = '../data/IMB_Lei_PANGAEA/*/*/'
fname = glob(inpath+'2019T66*.tab')[0]
print(fname)

time = getColumn(fname,0,skipheader=27,delimiter='\t')
dt_thi = [ datetime.strptime(time[x], "%Y-%m-%dT%H:%M") for x in range(len(time)) ]
#print(dt_thi)

it = getColumn(fname,3,skipheader=27,delimiter='\t')
sd = getColumn(fname,4,skipheader=27,delimiter='\t')

it = np.array(it,dtype=float)
sd = np.array(sd,dtype=float)

#plot
y = np.arange(0,tdata.shape[1])
#turn around the y axis
plt.ylim(y[-1],y[0])
#convert thermister number to distance in m
yt = np.arange(0,tdata.shape[1]*0.02,.5)
plt.yticks(y[::25], yt)
#dummy x-axis
x = mdates.date2num(dt_temp)

##temperatures
#plt.pcolor(x,y,tdata.T, cmap=plt.cm.RdYlBu_r, vmin=-30, vmax=0)

#contours on melting sea water temperatures
plt.contour(x,y,tdata.T, levels=[0], c='g')

#interfaces
#estimate where the snow-ice interface was initially
#scale to thermistors (in cm)
ife=1
snowline=(ife-sd)/.02
iceline=(ife+it)/.02

plt.plot(dt_thi,np.ones_like(snowline)*ife/.02,c='k',ls=':')
plt.plot(dt_thi,snowline,c='w')
plt.plot(dt_thi,iceline,c='w')

#plt.autofmt_xdate()
#plt.colorbar()
plt.show()

#air temperatures from both buoys
#get mean temperature up to 10cm over the snowline
topt=20
mask = (tdata[:,:topt]<-50) | (tdata[:,:topt]>10)
air_t = np.mean(np.ma.array(tdata[:,:topt],mask=mask),axis=1)

plt.plot(dt_temp,air_t)
plt.plot(dt_temp,np.zeros_like(air_t),ls=':',c='k')
plt.show()

#prepare output for SnowModel

#make the full 3h time series for the SnowModel
temp = {'air_t': air_t}

df = pd.DataFrame(data=temp,index=dt_temp)
sums = df.resample('3H').mean().asfreq('3H')

#interpolation of nans
sums=sums.interpolate(method='polynomial',order=1)  #linear interpolation

air_t = sums.air_t.values
dates = sums.index.values

#convert back to datetime list
dt = dates.astype('O')
dt_temp = [ datetime.utcfromtimestamp(x/1e9) for x in dt ]

year = [ datetime.strftime(x, "%Y") for x in dt_temp ]
month = [ datetime.strftime(x, "%m") for x in dt_temp ]
day = [ datetime.strftime(x, "%d") for x in dt_temp ]
hour = [ datetime.strftime(x, "%H") for x in dt_temp ]

#time series text file exports
tt = [year,month,day,hour,air_t]
table = list(zip(*tt))

#save output
outpath = '../data/mosaic_buoy_data/'
outfile = outpath+'IMB_FYI_airt_3hr.csv'
print(outfile)

with open(outfile, 'wb') as f:
    #header
    f.write(b'year,month,day,air temperature (C)\n')
    np.savetxt(f, table, fmt="%s", delimiter=",")





