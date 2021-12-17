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
#loc = 'Sloop'
#dates = ['20191031','20191107','20191114','20191205',   '20191226','20200102','20200109','20200116','20200130','20200206','20200220','20200227','20200305','20200330','20200406','20200426','20200507']    #best data

#loc = 'Nloop'
#dates = ['20191024','20191031','20191107','20191114','20191121','20191128','20191205',  '20191219','20191226','20200102','20200109','20200116','20200130','20200206','20200220','20200227', '20200305','20200320','20200326','20200403','20200416','20200424','20200430','20200507']

#reference_date = '20200116'
#maxdist=25

#loc = 'snow1'
#dates = ['20191222','20200112','20200126','20200207','20200223','20200406']
#reference_date = '20200207'
#maxdist=10

loc = 'runway'
dates = ['20200112','20200207']
reference_date = '20200207'
maxdist=25

inpath_snow = '../data/MCS/MP/'
inpath_grid = '../data/grids_AGU/'
outpath = '../plots_AGU/'

#MP coordinates (for a day with good spacing!)
fn = glob(inpath_snow+'*/magnaprobe-transect-'+reference_date+'*'+loc+'-track-icecs-xy_corr.csv')[0]
x_track = getColumn(fn,3)
y_track = getColumn(fn,4)

x_track = np.array(x_track,dtype=np.float)
y_track = np.array(y_track,dtype=np.float)

#storage space
transect_snow = np.zeros((len(x_track),2+len(dates)))
transect_ice = np.zeros((len(x_track),2+len(dates)))
#print(transect_snow.shape)

transect_snow[:,0] = x_track
transect_snow[:,1] = y_track

transect_ice[:,0] = x_track
transect_ice[:,1] = y_track

dt_list=[]

for dd in range(0,len(dates)):
    date = dates[dd]
    #if date!='20200507':    #try to get this one right!
        #continue
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
    
    #work only with valid grid points
    invalid=np.isnan(i_grid)
    x_grid=np.ma.array(x_grid,mask=invalid).compressed()
    y_grid=np.ma.array(y_grid,mask=invalid).compressed()
    i_grid=np.ma.array(i_grid,mask=invalid).compressed()
    s_grid=np.ma.array(s_grid,mask=invalid).compressed()
    
    #np.set_printoptions(threshold=np.inf)
    #print(s_grid)
    #print(np.max(s_grid))
    ##exit()
    
    #print(i_grid.shape)

    #prepare place to store
    it = np.zeros_like(x_track)
    sd = np.zeros_like(x_track)
    
    #find nearest it,sd values to original MP points        
    for i in range(0,it.shape[0]):
        dx = x_track[i]-x_grid
        dy = y_track[i]-y_grid                  
        dg = np.sqrt(dx**2+dy**2)
        
        far=dg>maxdist
        dgf = np.ma.array(dg,mask=far).compressed()
        ic = np.ma.array(i_grid,mask=far).compressed()
        sc = np.ma.array(s_grid,mask=far).compressed()
        
        #find nearest tt and it value
        try:
            nn = np.argmin(dgf)
            it[i] = ic[nn]
            sd[i] = sc[nn]
            #print(i,x_track[i],y_track[i],it[i])

        except:
            #print(np.min(dg))
            it[i] = np.nan
            sd[i] = np.nan
            continue
 
    transect_snow[:,dd+2] = sd
    transect_ice[:,dd+2] = it
    
    print(np.ma.array(it,mask=it==0).compressed().shape)

    #plt.plot(it)
    plt.plot(sd)
plt.show()

#transect_snow=np.where(transect_snow==0,np.nan,transect_snow)
#transect_ice=np.where(transect_ice==0,np.nan,transect_ice)

#save the data
ouf = inpath_grid+loc+'_'+stp+'m_'+method_gem2+ch_name+'_track2.npz'

with open(ouf, 'wb') as f:
    np.savez(f, dates = dates, snow = transect_snow, ice = transect_ice)


