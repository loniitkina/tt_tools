import numpy as np
from glob import glob
from tt_func import getColumn, running_stats, get_ice_mode
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
from datetime import datetime, timedelta




#weather
fname = inpath_weather+'weather_Oct-Jul.csv'
print(fname)
date = getColumn(fname,0, delimiter=',')
date = [ datetime.strptime(x, '%Y/%m/%d %H:%M:%S') for x in date ]
wind = getColumn(fname,7, delimiter=',')
wind = np.array(wind,dtype=np.float)
wind = savgol_filter(wind, window, polyorder)

windd = getColumn(fname,6, delimiter=',')
windd = np.array(windd,dtype=np.float)
windd = savgol_filter(windd, window, polyorder)

temp = getColumn(fname,4, delimiter=',')
temp = np.array(temp,dtype=np.float)
temp = savgol_filter(temp, window, polyorder)

#precipitation
fname=inpath_ARM+'precipitation_events.csv'
print(fname)
date_p = getColumn(fname,0, delimiter=',')
date_p = [ datetime.strptime(x, '%Y-%m-%dT%H:%M:%S') for x in date_p ]
precip = getColumn(fname,1, delimiter=',')
precip = np.array(precip,dtype=np.float)

#plotting the time series

#spacing between the box plots
dt = [ datetime.strptime(x, '%Y%m%d') for x in dates ]
dt_diff = [ (x-dt[0]).days for x in dt ]
dt_diff_off1 = [ (x-dt[0]).days+2 for x in dt ]
dt_diff_off2 = [ (x-dt[0]).days+4 for x in dt ]
cx[0].set_xlim(-2,dt_diff[-1]+7)  #first date here: 20191031, last date:20200507

#snow on level ice
bp1=cx[0].boxplot(ts_level_si, notch=True, showfliers=False, positions=dt_diff,widths=2,patch_artist=True,
            boxprops=dict(facecolor='purple',alpha=.4))

#snow in rubble
bp2=cx[0].boxplot(ts_rubble_si, notch=True, showfliers=False, positions=dt_diff_off1,widths=2,patch_artist=True,
            boxprops=dict(facecolor=colors[2],alpha=.4))

#snow in ridges
bp3=cx[0].boxplot(ts_ridge_si, notch=True, showfliers=False, positions=dt_diff_off2,widths=2,patch_artist=True,
            boxprops=dict(facecolor=colors[4],alpha=.4))

#and a dirty trick for the X axis
dates_m = ['20191101','20191201','20200101','20200201','20200301','20200401','20200501']
dt_m = [ datetime.strptime(x, '%Y%m%d') for x in dates_m ]
dt_diff = [ (x-dt[0]).days for x in dt_m ]
cx[0].set_xticks(dt_diff)
cx[0].set_xticklabels(['2019-11','2019-12','2020-01','2020-02','2020-03','2020-4','2020-5'])

cx[0].legend([bp1["boxes"][0], bp2["boxes"][0], bp3["boxes"][0]], ['level', 'rubble', 'ridges'], loc='upper left', fontsize=15,ncol=3)


#surface type fractions
cx[1].plot(dt_list,ts_level_frac,color='purple',ls='-',label='level')
cx[1].plot(dt_list,ts_rubble_frac,color=colors[2],ls='-',label='rubble')
cx[1].plot(dt_list,ts_ridge_frac,color=colors[4],ls='-',label='ridge')
cx[1].legend(fontsize=15,ncol=3)

#correlations
cx[2].plot(dt_list_s,r2_ts,color='k',ls=':',label='thermodyn. driver')
cx[2].scatter(dt_list[:4],r2_ts[:4], s=150, facecolors='none', edgecolors='r')     #red circle for negative correlation
cx[2].plot(dt_list_s,r2_ts_roughness,color='k',ls='--',label='dyn. driver')
cx[2].legend(fontsize=15,ncol=2)


#air temperature
cx[3].set_ylabel('Temperature (C)', fontsize=20)
cx[3].tick_params(axis="x", labelsize=14)
cx[3].tick_params(axis="y", labelsize=14)
cx[3].set_xlim(start,end)

cx[3].plot(date,temp,c='darkred')

#wind speed and direction
cx[4].set_ylabel('Wind Speed (m/s)', fontsize=20)
cx[4].tick_params(axis="x", labelsize=14)
cx[4].tick_params(axis="y", labelsize=14)
cx[4].set_xlim(start,end)

cs = cx[4].scatter(date,wind,c=windd,cmap=plt.cm.twilight)
cb = plt.colorbar(cs,orientation='horizontal',aspect=80, fraction=.05, pad=.1)  # draw colorbar
cb.set_label(label='Wind direction (deg.)',fontsize=15)

#horizontal line for drifting snow limit (7.7m/s based on dry snow estimate of Li and Pomeroy, 1997)
driftsnow=np.ones_like(wind)*7.7
cx[4].plot(date,driftsnow,c='k')

#precipitation
cx[4].plot(date_p,precip,'*',c='b')
cx[4].set_ylim(0,15)

#fig2.autofmt_xdate()

fig2.savefig(outpath+'r2_ts1'+suff+'_'+loc,bbox_inches='tight')
