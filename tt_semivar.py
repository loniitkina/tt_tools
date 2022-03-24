import numpy as np
from glob import glob
from tt_func import getColumn, semivar, polymodel
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from scipy.fft import fft, fftfreq

#this script always takes all dates in the '_track.npz' file (list of dates must be identical to the one in tt_grid_roll.py)!
#if you dont want some dates, skip in the script!

#optional outputfileme suffix
suff=''

#location and dates
title='Southern transect loop '
loc = 'Sloop'

dates = ['20191031','20191107','20191114','20191205',   '20191226','20200102','20200109','20200116','20200130','20200206','20200220','20200227','20200305','20200330','20200406','20200426','20200507']

selection = ['20191031','20191205','20200220','20200227','20200330','20200426']
selection = ['20191031','20191107','20191114','20191205',   '20191226','20200102','20200109','20200116','20200130','20200206','20200220','20200227','20200305','20200330','20200426']#,'20200507'] #paralel is missing data on 6 april and 7 may

selection = ['20191031','20191107','20191114','20191205','20200102','20200109','20200130','20200220','20200227','20200305','20200330','20200426']  #best data

#loc = 'Nloop'
#dates =['20191024','20191031','20191107','20191114','20191121','20191128','20191205',  '20191219','20191226','20200102','20200109','20200116','20200130','20200206','20200220','20200227', '20200305','20200320','20200326','20200403','20200416','20200424','20200430','20200507']

#title='Snow1 transect '
#loc= 'snow1'
#dates = ['20191222','20200112','20200126','20200207','20200223','20200406']    #20200126,20200406  are reduced tracks
#selection = dates


mix=True
mix=False

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
outpath = '../plots_gridded/'

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

fig3 = plt.figure(figsize=(18,5))
fx = fig3.add_subplot(122)
fx.set_xlabel('Frequency ($m^{-1}$)', fontsize=20)
fx.set_ylabel('Signal amplitude (m)', fontsize=20)

gx = fig3.add_subplot(121)
gx.set_xlabel('Frequency ($m^{-1}$)', fontsize=20)
gx.set_ylabel('Signal amplitude (m)', fontsize=20)

fx.set_ylim(0,.1)
fx.set_xlim(0.0066,.2)
fx.set_xscale('log')
fx.set_xticks([0.0066,0.01,.0142,.02,.0286,.04,.066,.1,.143,0.2])
fx.set_xticklabels([r'$\frac{1}{150}$',r'$\frac{1}{100}$',r'$\frac{1}{70}$',r'$\frac{1}{50}$',r'$\frac{1}{35}$',r'$\frac{1}{25}$',r'$\frac{1}{15}$',r'$\frac{1}{10}$',r'$\frac{1}{7}$',r'$\frac{1}{5}$'])

gx.set_ylim(0,.2)
#gx.set_xlim(0.013,.2)
gx.set_xlim(0.0066,.2)  #from 150m to 5m!
gx.set_xscale('log')
gx.set_xticks([0.0066,0.01,.0142,.02,.0286,.04,.066,.1,.143,0.2])
gx.set_xticklabels([r'$\frac{1}{150}$',r'$\frac{1}{100}$',r'$\frac{1}{70}$',r'$\frac{1}{50}$',r'$\frac{1}{35}$',r'$\frac{1}{25}$',r'$\frac{1}{15}$',r'$\frac{1}{10}$',r'$\frac{1}{7}$',r'$\frac{1}{5}$'])






#fx.set_yscale('log')
#gx.set_yscale('log')

for dd in range(0,len(dates)):
    date = dates[dd]
    dt = datetime.strptime(date, '%Y%m%d')
    dt_list.append(dt)
    print(date)
    
    inf = inpath_grid+loc+'_'+stp+'m_'+method_gem2+ch_name+'_track.npz'
    inf = inpath_grid+loc+'_'+stp+'m_'+method_gem2+ch_name+'_track1.npz'
    inf = inpath_grid+loc+'_'+stp+'m_'+method_gem2+ch_name+'_track2.npz'
    data = np.load(inf)

    transect_snow = data['snow']
    transect_ice = data['ice']
    
    mxx = transect_snow[:,0]    #these are MP coordinates from 20200116
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
    #ax.set_title('All level ice - several lines', fontsize=25)
    
    if loc=='Sloop':
        #mask = (x<0) | (x>600)  #| (it>2)  #level ice is never > 2m, some rubble and ridges are just between 2 and 3 m thick!)
        #suff='_all'
        
        ##parallel to ship heading
        #mask = (x<0) | (x>260)  #| (it>2)
        #suff='_par'
        ##fx.set_xlim(0.0038,.2)  #this side is a bit longer
        ##gx.set_xlim(0.0038,.2)
        
        ##perpendicular to ship heading
        ##mask = (x<262) | (x>435)  #| (it>2)
        #mask = (x<260) | (x>440)
        #suff='_per'
        
        #diagonal to ship heading
        mask = (x<440) | (x>600)  #| (it>2)
        suff='_dia'

        
    if loc=='snow1':
        mask = it>2
    
    ##parallel to ship heading
    #mask = (x<100) | (x>260)  | (it>2)
    
    ##perpendicular to ship heading
    #mask = (x<262) | (x>435)  | (it>2)
    
    ##other level ice
    #mask = (x<435) | (x>750)  | (it>2)
    
    ##all ridges and rubble
    #mask = ~((x<100) | (x>750))
    
    ##only same direction/line across ridges
    #ax.set_title('Ridges and Rubble - straight line', fontsize=25)
    #mask = (x<900) | (x>1300)

    it = np.ma.array(it,mask=mask).compressed()
    si = np.ma.array(si,mask=mask).compressed()
    mxx = np.ma.array(mxx,mask=mask).compressed()
    myy = np.ma.array(myy,mask=mask).compressed()
    
    print(it.shape)
    
    if mix:
        
        #snow1
        #asign a similar date
        if date=='20191226':
            ds=0
        elif date=='20200109':
            ds=1
        elif date=='20200130':
            ds=2
        elif date=='20200220':
            ds=3
        elif date=='20200227':
            ds=4
        elif date=='20200406':
            ds=5
        else:
            ds=-1   #no similar date
            
        if ds>-1:
            print('combi mix')
            loc1='snow1'
            
            inf = inpath_grid+loc1+'_'+stp+'m_'+method_gem2+ch_name+'_track.npz'
            data = np.load(inf)

            transect_snow = data['snow']
            transect_ice = data['ice']
            
            mxx_s = transect_snow[:,0]    #these are MP coordinates from xxxxxx
            myy_s = transect_snow[:,1]
            si_s = transect_snow[:,ds+2]
            it_s = transect_ice[:,ds+2]
            
            #add snow1 to Sloop data
            mxx=np.append(mxx,mxx_s); myy=np.append(myy,myy_s)
            si=np.append(si,si_s)
            it=np.append(it,it_s)
    
    it = np.ma.masked_invalid(it)
    si = np.ma.array(si,mask=it.mask)
    
    mxx = np.ma.array(mxx,mask=it.mask); mxx = mxx.compressed()
    myy = np.ma.array(myy,mask=it.mask); myy = myy.compressed()
    
    si = si.compressed()
    it = it.compressed()
    
    #plot the map
    cx.plot(mxx,myy,'o',ms=1,label=date)
    
    if date in selection:
        print('selected date: '+date)

        #==================================================
        #snow depth
        
        #semivar
        #sum of all squares of all differences between measurements inside each of the loops - divided by sample number and halved (semi-variogram)
        #normally, they can be done in 3-d, but in our case the distance is just along the track
        
        h=.75
        lim=30                      #max for lim: 200m is roughly the radius of the loop => 2*Pi*r=1300m ~total loop lenght
        
        maxd,semivar_si = semivar(h,lim,si,mxx,myy)
        
        #plotting
        ax.scatter(maxd,semivar_si,s=1, color=colors[dd])
        
        #fit semivar model    
        xmodel,ymodel = polymodel(maxd,semivar_si,lim,3)
        ax.plot(xmodel, ymodel, color=colors[dd],ls='-',label=date,alpha=.9,lw=3)
    
        #Fourier transform (discrete)
        #number of sample points
        N = si.shape[0]

        #sample spacing
        dx = mxx[1:]-mxx[:-1]
        dy = myy[1:]-myy[:-1]
        d = np.sqrt(dx**2+dy**2)
        T=np.mean(d)      #This is already gridded data!!!, default T=1
        #print(T)
        
        #signal
        y = si
        yf = fft(y)         #should we use fftn (instead of fft) to compute the DFT, since it has more than one dimension (map)?
        
        #frequency
        #unit: cycles/meter (5m=0.25,10m=.1,20m=0.05,30m=0.033,40m=0.025,5m=0.02) - larger values are shorter lenghts!!!
        #[:N//2] takes only real/positive part of the spectrum
        xf = fftfreq(N, T)[:N//2]   

        #plotting
        fx.plot(xf, 2.0/N * np.abs(yf[0:N//2]), color=colors[dd],label=date,alpha=.9,lw=3)
    
        #==================================================
        #ice thickness
        maxd,semivar_it = semivar(h,lim,it,mxx,myy)
        
        bx.scatter(maxd,semivar_it,s=1, color=colors[dd])
        
        xmodel,ymodel = polymodel(maxd,semivar_it,lim,3)
        bx.plot(xmodel, ymodel, color=colors[dd],ls='-',label=date,alpha=.9,lw=3)

        ##Fourier transform
        y = it
        yf = fft(y)
        xf = fftfreq(N, T)[:N//2]

        #plotting
        gx.plot(xf, 2.0/N * np.abs(yf[0:N//2]), color=colors[dd],label=date,alpha=.9,lw=3)

if mix:
    loc=loc+'_mix'
    
bx.legend(ncol=3)    
ax.legend(ncol=3)    
fig1.savefig(outpath+'semivar_'+str(step)+'_'+loc+suff)

cx.legend(ncol=3)    
fig2.savefig(outpath+'semivar_map_'+str(step)+'_'+loc+suff,bbox_inches='tight')

#make simple figure annotation
if suff=='_dia':
    fx.text(.004, .1, "h", ha="center", va="center", size=45)
    gx.text(.004, .2, "g", ha="center", va="center", size=45)
    
elif suff=='_per':
    fx.text(.004, .1, "f", ha="center", va="center", size=45)
    gx.text(.004, .2, "e", ha="center", va="center", size=45)
    
elif suff=='_par':
    fx.text(.004, .1, "d", ha="center", va="center", size=45)
    gx.text(.004, .2, "c", ha="center", va="center", size=45)
    
elif suff=='_all':
    fx.text(.004, .1, "b", ha="center", va="center", size=45)
    gx.text(.004, .2, "a", ha="center", va="center", size=45)


fx.grid()
gx.grid()
fx.legend(ncol=4)   
gx.legend(ncol=4)
fig3.savefig(outpath+'fft_'+str(step)+'_'+loc+suff,bbox_inches='tight')

    
