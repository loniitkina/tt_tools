import numpy as np
from glob import glob
from tt_func import getColumn, semivar, polymodel
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


#def loocv(x, y, fit, pred, deg):
    #"""LOOCV RSS for fitting a polynomial model."""
    #x = np.array(x); y = np.array(y)
    #n = len(x)
    #idx = np.arange(n)
    #rss = np.sum([(y - pred(fit(x[idx!=i], y[idx!=i], deg), x))**2.0 for i in range(n)])
    #return(rss)


#location and dates
loc = 'Sloop'
dates = ['20191031','20191107','20191114','20191205',   '20200102','20200109','20200116','20200130','20200206','20200220','20200227','20200305','20200330','20200426']#,'20200507']    #best data

dates = ['20191031','20191107','20191114','20191205',   '20191226','20200102','20200109','20200116','20200130','20200206','20200220','20200227','20200305','20200330','20200426','20200507']    #best data

dates = ['20191031','20191107','20191114','20191205',   '20191226','20200102','20200109','20200116','20200130','20200206','20200220','20200227','20200305','20200330','20200406','20200426','20200507']

#dates = ['20191031','20200130','20200507']

##early winter
#dates = ['20191031','20191107','20191114']
###deep winter
#dates = ['20191205','20200102','20200109','20200116','20200130','20200206','20200220']
###late winter
#dates = ['20200227','20200305','20200330','20200406','20200426','20200507']

#dense data
#dates = ['20200102','20200109','20200116','20200130','20200206','20200220','20200227']


title='Southern transect loop '

#loc = 'Nloop'
#dates =['20191024','20191031','20191107','20191114','20191121','20191128','20191205',  '20191219','20191226','20200102','20200109','20200116','20200130','20200206','20200220','20200227', '20200305','20200320','20200326','20200403','20200416','20200424','20200430','20200507']

##early
#dates =['20191024','20191031','20191107','20191114','20191121','20191128']
##mid
#dates =['20191205',  '20191219','20191226','20200102','20200109','20200116','20200130','20200206','20200220']
##late
#dates =['20200227', '20200305','20200320','20200326','20200403','20200416','20200424','20200430','20200507']


#loc= 'snow1'
#dates = ['20191222','20200112','20200126','20200207']    #20200126 is reduced track (square!)
#datel = ['2019/12/22','2020/01/12','2020/01/26','2020/02/07']
#title='Snow1 transect '

#loc = 'runway'
#dates = ['20200207']
#datel = ['2020/02/07']
#title='Runway transect '



#loc= 'special'
#dates = ['20200123']
#datel = ['2020/01/23']
#title='Long transect '

print(loc)
colors = plt.cm.rainbow(np.linspace(0, 1, len(dates)))
#colors = plt.cm.Blues(np.linspace(0, 1, len(dates)))

if len(dates) == 1:
    colors = ['.1','.5']
    

inpath_table = '../data/MCS/MP/'
inpath_weather = '../data/weather/'
inpath_grid = '../data/grids_AGU/'
outpath = '../plots_AGU/'

step = 2
step = 1
stp = str(step)
method_gem2 = 'nearest'
#method_gem2 = 'linear'
ch_name = '_18kHz'


std_list=[]
si_list=[]
it_list=[]
dt_list=[]

r2_ts=[]
spacing_ts=[]
nit_ts=[]

#init a plot
fig1 = plt.figure(figsize=(10,10))
fig1.patch.set_facecolor('0.5')

ax = fig1.add_subplot(211)
ax.set_xlabel('Distance (m)', fontsize=20)
#ax.set_title(title+datel[dd], fontsize=25)
ax.set_ylabel('Snow semi-variance (m)', fontsize=20)
ax.tick_params(axis="x", labelsize=14)
ax.tick_params(axis="y", labelsize=14)

bx = fig1.add_subplot(212)
bx.set_xlabel('Distance (m)', fontsize=20)
#bx.set_title(title+datel[dd], fontsize=25)
bx.set_ylabel('Ice semi-variance (m)', fontsize=20)
bx.tick_params(axis="x", labelsize=14)
bx.tick_params(axis="y", labelsize=14)

fig2 = plt.figure(figsize=(10,10))
cx = fig2.add_subplot(111)

for dd in range(0,len(dates)):
    date = dates[dd]
    dt = datetime.strptime(date, '%Y%m%d')
    dt_list.append(dt)
    print(date)
    
    #outname = 'profile_'+date+'_'+loc+'gridded.png'
    
    ##choose one 'most perfct' MP track to compare to the others
    #fname = glob(inpath_table+'*/magna+gem2-transect-'+date+'*'+loc+'.csv')[0]
    #print(fname)
    #mxx = getColumn(fname,3, delimiter=',', magnaprobe=False)
    #myy = getColumn(fname,4, delimiter=',', magnaprobe=False)
    #snod = getColumn(fname,5, delimiter=',', magnaprobe=False)
    #it = getColumn(fname,6, delimiter=',', magnaprobe=False)
    #mxx = np.array(mxx,dtype=np.float)
    #myy = np.array(myy,dtype=np.float)
    #si = np.array(snod,dtype=np.float)
    #it = np.array(it,dtype=np.float)
    
    inf = inpath_grid+loc+'_'+stp+'m_'+method_gem2+ch_name+'_track_test.npz'
    inf = inpath_grid+loc+'_'+stp+'m_'+method_gem2+ch_name+'_track.npz'
    
    data = np.load(inf)

    transect_snow = data['snow']
    transect_ice = data['ice']
    
    mxx = transect_snow[:,0]
    myy = transect_snow[:,1]
    si = transect_snow[:,dd+2]
    it = transect_ice[:,dd+2]
    
    #accounting for diffent wind direction in the Sloop
    #level ice and 2 different directions in the first 700m
    
    #get distances between points
    dx = mxx[1:]-mxx[:-1]
    dy = myy[1:]-myy[:-1]
    md = np.sqrt(dx**2+dy**2)
    x = np.zeros_like(si)
    x[1:] = np.cumsum(md)
    
    #all level ice between 200 and 700m distance - level ice always thinner than 1m
    ax.set_title('All level ice - several lines', fontsize=25)
    mask = (x<100) | (x>750)  | (it>2)
    
    ##parallel to ship heading
    #mask = (x<100) | (x>260)  | (it>3)
    
    ##perpendicular to ship heading
    #mask = (x<262) | (x>435)  | (it>2)
    
    ##all ridges and rubble
    #mask = ~((x<100) | (x>750))
    
    ##only same direction/line across ridges
    #ax.set_title('Ridges and Rubble - straight line', fontsize=25)
    #mask = (x<900) | (x>1300)

    it = np.ma.array(it,mask=mask).compressed()
    si = np.ma.array(si,mask=mask).compressed()
    mxx = np.ma.array(mxx,mask=mask).compressed()
    myy = np.ma.array(myy,mask=mask).compressed()
    
    cx.plot(mxx,myy,'o',ms=1,label=date)
    plt.show()
        
    it = np.ma.masked_invalid(it)
    si = np.ma.array(si,mask=it.mask)
    
    mxx = np.ma.array(mxx,mask=it.mask); mxx = mxx.compressed()
    myy = np.ma.array(myy,mask=it.mask); myy = myy.compressed()
    
    si = si.compressed()
    it = it.compressed()
    
    #sum of all squares of all differences between measurements inside each of the loops - divided by sample number and halved (semi-variogram)
    #normally, they can be done in 3-d, but in our case the distance is just along the track
    
    h=.75
    lim=30                      #max for lim: 200m is roughly the radius of the loop => 2*Pi*r=1300m ~total loop lenght
    maxd = np.arange(0,lim,h)
    
    semivar_si = semivar(h,lim,maxd,si,mxx,myy)
    
    #plotting
    ax.scatter(maxd,semivar_si,s=1, color=colors[dd])
    
    #fit semivar model    
    xmodel,ymodel = polymodel(maxd,semivar_si,lim,3)
    ax.plot(xmodel, ymodel, color=colors[dd],ls='-',label=date)
    
    #some bad ice data - dont plot:
    if date=='20191226' or date=='20200116' or date=='20200206' or date=='20200507':
        continue
    
    else:
        semivar_it = semivar(h,lim,maxd,it,mxx,myy)
        
        bx.scatter(maxd,semivar_it,s=1, color=colors[dd])
        
        xmodel,ymodel = polymodel(maxd,semivar_it,lim,3)
        bx.plot(xmodel, ymodel, color=colors[dd],ls='-',label=date)

bx.legend(ncol=3)    
ax.legend(ncol=3)    
fig1.savefig(outpath+'semivar_'+str(step))

cx.legend(ncol=3)    
fig2.savefig(outpath+'semivar_map_'+str(step))



    
