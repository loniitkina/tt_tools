import numpy as np
from glob import glob
from tt_func import getColumn, semivar, polymodel
from scipy import ndimage
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


#step = 2        #grid spacing in meters 
step = 1
stp = str(step)
method_gem2 = 'nearest'
#method_gem2 = 'linear'
ch_name = '_18kHz'

#location and dates
loc = 'Sloop'
dates = ['20191031','20191107','20191114','20191205',   '20191226','20200102','20200109','20200116','20200130','20200206','20200220','20200227','20200305','20200330','20200406','20200426','20200507']    #best data

loc = 'Nloop'
dates = ['20191024','20191031','20191107','20191114','20191121','20191128','20191205',  '20191219','20191226','20200102','20200109','20200116','20200130','20200206','20200220','20200227', '20200305','20200320','20200326','20200403','20200416','20200424','20200430','20200507']



inpath_snow = '../data/MCS/MP/'
inpath_grid = '../data/grids_AGU/'
outpath = '../plots_AGU/'

#MP coordinates (for a day with good spacing!)
fn = glob(inpath_snow+'*/magnaprobe-transect-'+'20200116'+'*'+loc+'-track-icecs-xy_corr.csv')[0]
x_track = getColumn(fn,3, delimiter=',', magnaprobe=False)
y_track = getColumn(fn,4, delimiter=',', magnaprobe=False)

x_track = np.array(x_track,dtype=np.float)
y_track = np.array(y_track,dtype=np.float)

#storage space
transect_snow = np.zeros((len(x_track),2+len(dates)))
transect_ice = np.zeros((len(x_track),2+len(dates)))
#print(transect_snow.shape)

transect_snow[:,0] = x_track
transect_snow[:,1] = y_track

dt_list=[]

for dd in range(0,len(dates)):
    date = dates[dd]
    dt = datetime.strptime(date, '%Y%m%d')
    dt_list.append(dt)
    print(date)
    
    #load data
    inf = inpath_grid+loc+'_'+date+'_'+stp+'m_'+method_gem2+ch_name+'_adjusted.npz'
    print(inf)
    
    data = np.load(inf)
    x_grid = data['x']
    y_grid = data['y']
    s_grid = data['snow']
    i_grid = data['ice']
    
    it = np.zeros_like(x_track)
    sd = np.zeros_like(x_track)
    #find nearest tt and it values to original mp/sd points        
    for i in range(0,it.shape[0]):
        dx = x_track[i]-x_grid
        dy = y_track[i]-y_grid                  
        dg = np.sqrt(dx**2+dy**2)
        dgf = dg.flatten()
        
        #find nearest tt and it value
        nn = np.argmin(dgf)
        it[i] = i_grid.flatten()[nn]
        sd[i] = s_grid.flatten()[nn]

        #there can be nans...
        #replace with mean in the closest n values
        n=3
        while (np.isnan(it[i]) and n < 400):    #100 values is just 20x20m on 2-m grid!!! - largest spatial problems are with first transects - level snow/ice
            nn = np.argpartition(dgf,n)[:n]
            tmp_it = i_grid.flatten()[nn]
            tmp_sd = s_grid.flatten()[nn]

            it[i] = np.mean(np.ma.masked_invalid(tmp_it))
            sd[i] = np.mean(np.ma.masked_invalid(tmp_sd))

            n = n+5                             #add x new values at each step
 
    transect_snow[:,dd+2] = sd
    transect_ice[:,dd+2] = it

    plt.plot(it)
    plt.plot(sd)
plt.show()

#save the data
ouf = inpath_grid+loc+'_'+stp+'m_'+method_gem2+ch_name+'_track.npz'

with open(ouf, 'wb') as f:
    np.savez(f, dates = dates, snow = transect_snow, ice = transect_ice)


