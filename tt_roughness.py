import numpy as np
from glob import glob
from tt_func import getColumn, running_stats, get_ice_mode
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import matplotlib.dates as mdates

##grid parameters
#stp = '5m'
#stp = '2m_linear'
#stp = '2m_nearest'
#maxdist = 10   #how far away to search in case of nan
##maxdist = 5

#window size for savgol smoothing savgol_filter (must be odd and more than polyorder=3)
polyorder=3
window=231


#location and dates - if gridded data is used these dates have to correspond to the dates in tt_grid_roll.py
loc = 'Sloop'
dates = ['20191031','20191107','20191114','20191205',   '20191226','20200102','20200109','20200116','20200130','20200206','20200220','20200227','20200305','20200330','20200406','20200426','20200507']
title='Southern transect loop '

selection = ['20191031','20191107','20191114','20191205','20200102','20200109','20200130','20200220','20200227','20200305','20200330','20200406','20200426','20200507']  #best data


#loc = 'Nloop'
#dates =['20191024','20191031','20191107','20191114','20191121','20191128','20191205',  '20191219','20191226','20200102','20200109','20200116','20200130','20200206','20200220','20200227', '20200305','20200320','20200326','20200403','20200416','20200424','20200430','20200507']

#selection=['20191024','20191128','20191205',  '20191219','20200102','20200109','20200130','20200220','20200227', '20200305','20200320','20200326','20200403','20200424','20200430','20200507']

#loc= 'snow1'
#dates = ['20191222','20200112','20200126','20200207']    #20200126 is reduced track (square!)
#title='Snow1 transect '

#loc= 'runway'
#dates = ['20200112','20200207']
#title='Runway transect '
#selection=dates

#loc= 'special'
#dates = ['20200123']
#title='Long transect '

#loc= 'special'
#dates = ['20200617']
#title='leg 4 initial survey  '
#selection = ['20200617']

#loc= 'transect'
#dates = ['20200617','20200627','20200629','20200630','20200703','20200704','20200705','20200706','20200707','20200708','20200710','20200714','20200719','20200720','20200725','20200726']
#title='leg 4 transect  '
#selection = ['20200617','20200630','20200704','20200706','20200710','20200714','20200725','20200726']
#selection = dates

gridded=True
#gridded=False

print(loc)
colors = plt.cm.rainbow(np.linspace(0, 1, len(dates)))
#colors = plt.cm.Blues(np.linspace(0, 1, len(dates)))

if len(dates) < 5:
    colors = plt.cm.rainbow(np.linspace(0, 1, 5))
    

inpath_table = '../data/MCS/MP/'
inpath_grid = '../data/grids_AGU/'
inpath_weather = '../data/weather/'
inpath_ARM='../data/weather_ARM/'
outpath = '../plots_AGU/'
outpath = '../plots_gridded/'

step = 2
step = 1
stp = str(step)
method_gem2 = 'nearest'
#method_gem2 = 'linear'
ch_name = '_18kHz'

if gridded==False:
    suff='original'
else:
    suff='gridded_'+str(step)


dt = [ datetime.strptime(x, '%Y%m%d') for x in dates ]
datel = [ datetime.strftime(x, '%Y/%m/%d') for x in dt ]

#what about working with some 'dune footprint' - similar to range in semi-variogram, typically 5-10
dune_range=np.ones_like(dt)*50    #empirically estimated from FTT (mean for ice and snow) and observations about ridge influence in nature
#dune_range=[45,45,45,14,20,20,20,20,20,20,20,30,30,30,30,30,30]  #empirically estimated from semi-varigram

#Rougness scatter plot
fig4 = plt.figure(figsize=(10,10))
ax = fig4.add_subplot(111)
#ax.set_title(title, fontsize=25)
ax.text(-.08, .8, "a", ha="center", va="center", size=35)  #make simple figure annotation
ax.set_xlabel('Roughness (m)', fontsize=20)
ax.set_ylabel('Snow (m)', fontsize=20)
ax.tick_params(axis="x", labelsize=14)
ax.tick_params(axis="y", labelsize=14)
ax.set_xlim(0,1)
ax.set_ylim(0,.8)

#Thermodynamics scatter plot
fig1 = plt.figure(figsize=(10,10))
fig1.patch.set_facecolor('0.5')
bx = fig1.add_subplot(111)
bx.set_xlabel('Snow (m)', fontsize=20)
#bx.set_title(title, fontsize=25)
bx.text(-.05, 2, "b", ha="center", va="center", size=35)  #make simple figure annotation
bx.set_ylabel('Ice (m)', fontsize=20)
bx.tick_params(axis="x", labelsize=14)
bx.tick_params(axis="y", labelsize=14)
#ax.set_facecolor('0.3')
bx.set_xlim(0,.5)
bx.set_ylim(0,2)

#The time series plot
fig2, cx = plt.subplots(5, 1, gridspec_kw={'height_ratios': [1,.5,.5,.5,1]},figsize=(10,15))
fig2.tight_layout()

start = datetime(2019, 10, 29, 0, 0)
end = datetime(2020, 5, 15, 0, 0)

#snow PDFs
cx[0].set_ylabel('Snow depth (m)', fontsize=20)
cx[0].tick_params(axis="x", labelsize=14)
cx[0].tick_params(axis="y", labelsize=14)
cx[0].set_ylim(0,1)

#surface type fractions
cx[1].text(mdates.date2num(start)-23, 1, "b", ha="center", va="center", size=35)  #make simple figure annotation
cx[1].set_ylabel('Fraction', fontsize=20)
cx[1].tick_params(axis="x", labelsize=14)
cx[1].tick_params(axis="y", labelsize=14)
cx[1].set_xlim(start,end)
cx[1].set_ylim(0,1)

#correlations
cx[2].text(mdates.date2num(start)-23, .8, "c", ha="center", va="center", size=35)  #make simple figure annotation
cx[2].set_ylabel('$R^2$', fontsize=20)
cx[2].tick_params(axis="x", labelsize=14)
cx[2].tick_params(axis="y", labelsize=14)
cx[2].set_xlim(start,end)


std_list=[]
si_list=[]
it_list=[]
dt_list=[]
dt_list_s=[]

r2_ts=[]
r2_ts_roughness=[]
r2_ts_roughness2=[]
spacing_ts=[]
total_l=[]
nit_ts=[]

ts_level_si=[]
ts_rubble_si=[]
ts_ridge_si=[]

ts_level_it=[]
ts_rubble_it=[]

ts_level_frac=[]
ts_rubble_frac=[]
ts_ridge_frac=[]

for dd in range(0,len(dates)):
    date = dates[dd]
    dt = datetime.strptime(date, '%Y%m%d')
    dt_list.append(dt)
    print(date)
    
    #outname = 'profile_'+date+'_'+loc+'gridded.png'
        
    if gridded==False:
    
        #choose one 'most perfct' MP track to compare to the others
        fname = glob(inpath_table+'*/magna+gem2-transect-'+date+'*'+loc+'.csv')[0]
        if date=='20200617' and loc=='special':
            fname = glob(inpath_table+'*/magna+gem2-transect-'+date+'*'+loc+'.csv')[1]  #two special surverys on same date
        
        print(fname)
        mxx = getColumn(fname,3)
        myy = getColumn(fname,4)
        snod = getColumn(fname,5)
        #mpd = getColumn(fname,6)   #melt pond depth
        it = getColumn(fname,8)
        mxx = np.array(mxx,dtype=np.float)
        myy = np.array(myy,dtype=np.float)
        si = np.array(snod,dtype=np.float)
        #mpd = np.array(mpd,dtype=np.float)
        it = np.array(it,dtype=np.float)
        
        #snow has -1 depth at melt pond surfaces in summer:
        si = np.where(si==-1,0,si)     
        
    else:
        #inf = inpath_grid+loc+'_'+stp+'m_'+method_gem2+ch_name+'_track_test.npz'
        #inf = inpath_grid+loc+'_'+stp+'m_'+method_gem2+ch_name+'_track1.npz'
        inf = inpath_grid+loc+'_'+stp+'m_'+method_gem2+ch_name+'_track2.npz'
        
        data = np.load(inf)

        transect_snow = data['snow']
        transect_ice = data['ice']
        
        mxx = transect_snow[:,0]
        myy = transect_snow[:,1]
        si = transect_snow[:,dd+2]
        it = transect_ice[:,dd+2]
        
    #clean up the nans
    it = np.ma.masked_invalid(it)
    si = np.ma.array(si,mask=it.mask)
    
    mxx = np.ma.array(mxx,mask=it.mask); mxx = mxx.compressed()
    myy = np.ma.array(myy,mask=it.mask); myy = myy.compressed()

    si = si.compressed()
    it = it.compressed()

            
    #get sea ice thickness mode
    irbins = np.arange(0,2,.06)
    mo = get_ice_mode(it,irbins)
    print(mo)
    thickice = mo+.3
    
    #get standard deviation of each magnaprobe point
    #based on standard deviation of closest 10 sea ice thickness measurements
    #first/last five measurements are not used
    
    #how many snow depth measurements points should be used
    #decide this based on the MP spacing, so that it is the same total distance for all legs/sampling personel
    
    if gridded==True:
        nit=50                  #very similar results in range 40-50 measurements (m)
                                #important for roughness correlation
                                #and 
        
    else:    
        dx = mxx[1:]-mxx[:-1]
        dy = myy[1:]-myy[:-1]
        print('MP measurement spacing:')
        spacing = np.mean(np.sqrt(dx**2+dy**2))
        print(spacing)
        spacing_ts.append(spacing)
        
        print('Total transect Lenght:')
        lenght = np.sum(np.sqrt(dx**2+dy**2))
        print(lenght)
        total_l.append(lenght)
        
        nit = int(30/spacing)   #take 50m distance as a starting point
        print(nit)
            
        dune_range[dd]=int(dune_range[dd]/spacing)
    
    nit_ts.append(nit)
    
    #running mean and variance
    itm,itv = running_stats(it,nit)
    std = np.sqrt(itv)
    
    sim,siv = running_stats(si,nit)    
    
    #first and last nit/2 values are zeros!!!
    std_whole = std.copy()
    mask = (sim==0) | np.isnan(sim) | np.isnan(std)
    
    std = np.ma.array(std,mask=mask).compressed()
    itm = np.ma.array(itm,mask=mask).compressed()
    sim = np.ma.array(sim,mask=mask).compressed()
    
    #truncated original snow depths
    #truncated original ice thickness
    sitrunc = np.ma.array(si,mask=mask).compressed()
    ittrunc = np.ma.array(it,mask=mask).compressed()

    #roughness scatter plot
    if date in selection:
        ax.scatter(std,sim,alpha=0.1,c=np.array([colors[dd]]))
        #ax.scatter(std,sitrunc,alpha=0.1,c=np.array([colors[dd]]))
    
    #r2 estimates
    x = std
    y = sim
    #y = sitrunc
    model = np.polyfit(x, y, 1)
    print('coefficients: ', model)
    
    if np.isnan(model[0]):
        r2_ts_roughness.append(0)
    else:
        predict = np.poly1d(model)
        from sklearn.metrics import r2_score
        r2 = r2_score(y, predict(x))
        print('R2 dyn: ',r2)
        
        x_lin_reg = np.arange(0, 1.1,.1)
        y_lin_reg = predict(x_lin_reg)
        if date in selection:
            ax.plot(x_lin_reg, y_lin_reg, c=colors[dd], label=datel[dd])
            
            cx[2].scatter(dt,r2,facecolors=colors[dd],s=70)
            
            ##get siginificance
            #from scipy.stats import linregress
            #print(linregress(x,y))
            #slope,intercept,rvalue,pvalue,stderr=linregress(x,y)
            ##p-value : two-sided p-value for a hypothesis test whose null hypothesis is that the slope is zero
            #if pvalue < 0.0001:
                #cx[2].scatter(dt,r2,marker='x',s=70)

        
            r2_ts_roughness.append(r2)
            dt_list_s.append(dt)
        
        
        #estimate the threshold values
        level=0
        rubble=0.1
        ridge=0.3
        
        ###leg 4 transect is very deformed, decrease criteria, to get at least some useful level ice data
        if loc=='transect':
            rubble=0.1
            ridge=0.3
        
        if loc=='Nloop':
            rubble=0.2
            ridge=0.3

        mask_level = std>rubble
        mask_ridge = (std<ridge) #| (itm<2.)
        mask_rubble = ~(mask_level & mask_ridge)
        
        #give snow volume for these classes
        #level ice
        y_pred = predict(level)
        level_mid = (level+rubble)/2
        print('level rough. value and predicted snow depth: ',level_mid,y_pred)
        #estimate the volume
        level_si = np.ma.array(sitrunc,mask=mask_level).compressed()
        ##also get level ice thickness for thermodyn. driver and SnowModel assimilation
        level_it = np.ma.array(ittrunc,mask=mask_level).compressed()
        vol = np.sum(level_si)/np.sum(sitrunc)
        print('volume fraction of level ice snow: ',vol)
        level_n = level_si.shape[0]/sitrunc.shape[0]
        print('fraction of level ice: ',level_n)
        
        #rubble
        rubble_mid = (rubble+ridge)/2
        y_pred = predict(rubble_mid)
        print('rubble rough. value and predicted snow depth: ',rubble_mid,y_pred)
        #estimate the volume
        rubble_si = np.ma.array(sitrunc,mask=mask_rubble).compressed()
        ##also get rubble ice thickness for SnowModel assimilation
        rubble_it = np.ma.array(ittrunc,mask=mask_rubble).compressed()
        vol = np.sum(rubble_si)/np.sum(sitrunc)
        print('volume fraction of rubble ice snow: ',vol)
        rubble_n = rubble_si.shape[0]/sitrunc.shape[0]
        print('fraction of rubble ice: ',rubble_n)

        #ridges
        ridge_mid = ridge*2
        y_pred = predict(ridge_mid)
        print('ridge rough. value and predicted snow depth: ',ridge_mid,y_pred)
        #estimate the volume
        ridge_si = np.ma.array(sitrunc,mask=mask_ridge).compressed()
        vol = np.sum(ridge_si)/np.sum(sitrunc)
        print('volume fraction of ridge ice snow: ',vol)
        ridge_n = ridge_si.shape[0]/sitrunc.shape[0]
        print('fraction of ridge ice: ',ridge_n)
        
        
        #store these for time series!
        ts_level_si.append(level_si)
        ts_rubble_si.append(rubble_si)
        ts_ridge_si.append(ridge_si)
        
        ts_level_frac.append(level_n)
        ts_rubble_frac.append(rubble_n)
        ts_ridge_frac.append(ridge_n)
        
        ts_level_it.append(level_it)
        ts_rubble_it.append(rubble_it)
        
        #print(ridge_si)
        
    
    ##snow depth derivative
    #x = std1
    #y = dsi1
    #model = np.polyfit(x, y, 1)
    #print('coefficients: ', model)
    
    #if np.isnan(model[0]):
        #r2_ts_roughness2.append(0)
    #else:
        #predict = np.poly1d(model)
        #from sklearn.metrics import r2_score
        #r2 = r2_score(y, predict(x))
        #print('R2: ',r2)
        
        #r2_ts_roughness2.append(r2)
         


    
    
    
    #thermodynamics plot
    #take all the roughness < 0.1 and plot thickness against snow depth
    #thickice margin helps to mask the outliers - needs to be replaced by mode???

    #what about working with some 'dune footprint' - similar to range in semi-variogram*2, typically 15-45
    
    si,var = running_stats(si,dune_range[dd])   #n has to be divideable by 2
    it,var = running_stats(it,dune_range[dd])
    
    #si,var = running_stats(si,nit)   #n has to be divideable by 2
    #it,var = running_stats(it,nit)
    
    #from semivar
    #get distances between points
    dx = mxx[1:]-mxx[:-1]
    dy = myy[1:]-myy[:-1]
    md = np.sqrt(dx**2+dy**2)
    x = np.zeros_like(si)
    x[1:] = np.cumsum(md)
    
    #all level ice between 200 and 700m distance - level ice always thinner than 1m
    #ax.set_title('All level ice - several lines', fontsize=25)
    #mask = (x<100) | (x>750)  | (std_whole>rubble) | (si==0) #first and last values in running means are zeros!!!

    mask = (std_whole>rubble) | (si==0)

    si_level = np.ma.array(si,mask=mask).compressed()
    it_level = np.ma.array(it,mask=mask).compressed()
    
    #print(si_level)
    if len(si_level)==0:
        print('empty series')
        r2_ts.append(0)
        continue


    #plot
    ##running mean values
    if date in selection:
        #running means
        bx.scatter(si_level,it_level,alpha=0.1,c=colors[dd])
        x = si_level
        y = it_level

        ##original values
        #bx.scatter(level_si,level_it,alpha=0.1,c=colors[dd])
        #x=level_si
        #y=level_it
        
        model = np.polyfit(x, y, 1)
        print('coefficients: ', model)

        predict = np.poly1d(model)
        from sklearn.metrics import r2_score
        r2 = r2_score(y, predict(x))
        print('R2 thermo: ',r2)
        r2_ts.append(r2)

        x_lin_reg = np.arange(0, 1.1,.1)
        y_lin_reg = predict(x_lin_reg)
        
        print(x_lin_reg)
        print(y_lin_reg)

        #plot the linear regression model
        bx.plot(x_lin_reg, y_lin_reg, c=colors[dd], label=datel[dd])
        
        #plot the R2 time series
        cx[2].scatter(dt,r2,facecolors=colors[dd],s=70)
        
        ##get siginificance
        #from scipy.stats import linregress
        #print(linregress(x,y))
        #slope,intercept,rvalue,pvalue,stderr=linregress(x,y)
        ##p-value : two-sided p-value for a hypothesis test whose null hypothesis is that the slope is zero
        #if pvalue < 0.0001:
            #cx[2].scatter(dt,r2,marker='x',s=70)
        
        
        
        
        
    std_list.extend(std_whole)
    si_list.extend(si)
    it_list.extend(it)


#Roughness scatterplot
ax.legend(ncol=3)
fig4.savefig(outpath+'roughness_1'+suff+'_'+loc,bbox_inches='tight')
plt.close(fig4)


bx.legend(ncol=3)
fig1.savefig(outpath+'thermo_scatter_1'+suff+'_'+loc,bbox_inches='tight')
plt.close(fig1)




std_list = np.array(std_list)

mask = (std_list==0) | np.isnan(std_list)

std_list = np.ma.array(std_list,mask=mask)
si_list = np.ma.array(si_list,mask=mask)
it_list = np.ma.array(it_list,mask=mask)

std_list = std_list.compressed().tolist()
si_list = si_list.compressed().tolist()
it_list = it_list.compressed()

#print(std_list)
#print(si_list)
#print(it_list)


#linear regression!
import pandas as pd

ice = {'roughness': std_list,
            'snow': si_list}

ice_data = pd.DataFrame(data=ice)
#print(ice_data)

x = ice_data.roughness
y = ice_data.snow
model = np.polyfit(x, y, 1)

print(model)

predict = np.poly1d(model)
from sklearn.metrics import r2_score
r2 = r2_score(y, predict(x))
print(r2)


x_lin_reg = np.arange(0, 1,.1)
y_lin_reg = predict(x_lin_reg)

#fig3 = plt.figure(figsize=(10,10))
#ax = fig3.add_subplot(111)
#ax.set_xlabel('Roughness', fontsize=20)
#ax.set_title(title, fontsize=25)
#ax.set_ylabel('Snow', fontsize=20)
#ax.tick_params(axis="x", labelsize=14)


#ax.scatter(x, y,alpha=0.01)
#ax.plot(x_lin_reg, y_lin_reg, c = 'r')
#fig3.savefig(outpath+'roughness_all')


#time series of thermodynamics r2

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
inpath='../data/weather_Matrosov/mosaic-snowfall/'
fname=inpath+'precipitation_ARM_Matrosov_3h.csv'
print(fname)
date_y = getColumn(fname,0, delimiter=',')
date_m = getColumn(fname,1, delimiter=',')
date_d = getColumn(fname,2, delimiter=',')
date_h = getColumn(fname,3, delimiter=',')
date_p = [ date_y[x]+date_m[x]+date_d[x]+date_h[x] for x in range(0,len(date_y)) ]

date_p = [ datetime.strptime(x, '%Y%m%d%H') for x in date_p ]
precip = getColumn(fname,6, delimiter=',')      #KAZR Matrosov, mm/3h
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

cx[0].text(dt_diff[0]-25, 1, "a", ha="center", va="center", size=35)  #make simple figure annotation

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
cx[3].text(mdates.date2num(start)-23, 5, "d", ha="center", va="center", size=35)  #make simple figure annotation
cx[3].set_ylabel('Temperature (C)', fontsize=20)
cx[3].tick_params(axis="x", labelsize=14)
cx[3].tick_params(axis="y", labelsize=14)
cx[3].set_xlim(start,end)

cx[3].plot(date,temp,c='darkred')

#wind speed and direction
cx[4].text(mdates.date2num(start)-23, 15, "e", ha="center", va="center", size=35)  #make simple figure annotation
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

print(nit_ts)
print(spacing_ts)
print(total_l)


#separate time series of snow depth in level, rubble, ridges
fig5 = plt.figure(figsize=(20,5))
ax = fig5.add_subplot(111)
#ax.set_title(title, fontsize=25)
ax.set_ylabel('Snow depth (m)', fontsize=20)
ax.tick_params(axis="x", labelsize=14)
ax.tick_params(axis="y", labelsize=14)
ax.set_ylim(0,1)

#spacing between the box plots
dt = [ datetime.strptime(x, '%Y%m%d') for x in dates ]
dt_diff = [ (x-dt[0]).days for x in dt ]
dt_diff_off1 = [ (x-dt[0]).days+2 for x in dt ]
dt_diff_off2 = [ (x-dt[0]).days+4 for x in dt ]

#snow on level ice
bp1=ax.boxplot(ts_level_si, notch=True, showfliers=False, positions=dt_diff,widths=2,patch_artist=True,
            boxprops=dict(facecolor=colors[2],alpha=.4))

#snow in rubble
bp2=ax.boxplot(ts_rubble_si, notch=True, showfliers=False, positions=dt_diff_off1,widths=2,patch_artist=True,
            boxprops=dict(facecolor=colors[3],alpha=.4))

#snow in ridges
bp3=ax.boxplot(ts_ridge_si, notch=True, showfliers=False, positions=dt_diff_off2,widths=2,patch_artist=True,
            boxprops=dict(facecolor=colors[4],alpha=.4))

#and a dirty trick for the X axis
#dates_m = ['20191101','20191201','20200101','20200201','20200301','20200401','20200501']
#dt_m = [ datetime.strptime(x, '%Y%m%d') for x in dates_m ]
#dt_diff = [ (x-dt[0]).days for x in dt_m ]
#plt.xticks(dt_diff, ['1 Nov','1 Dec','1 Jan','1 Feb','1 Mar','1 Apr','1 May'])

#for whole MOSAiC annual cycle
dates_m = ['20190901','20191001','20191101','20191201','20200101','20200201','20200301','20200401','20200501','20200601','20200701','20200801']
dt_m = [ datetime.strptime(x, '%Y%m%d') for x in dates_m ]
dt_diff = [ (x-dt[0]).days for x in dt_m ]
plt.xticks(dt_diff, ['1 Sep','1 Oct','1 Nov','1 Dec','1 Jan','1 Feb','1 Mar','1 Apr','1 May','1 Jun','1 Jul','1 Aug'])

ax.set_xticks(dt_diff)
fig5.autofmt_xdate()

ax.legend([bp1["boxes"][0], bp2["boxes"][0], bp3["boxes"][0]], ['level ice', 'rubble ice', 'deformed ice'], loc='upper left', fontsize=20)
outname_ts_type='ts_'+loc+'_'+'1m_gridded_roughness_type.png'
fig5.savefig(outpath+outname_ts_type,bbox_inches='tight')


################################################################################################################################3
#write snow and ice values for different roughness categories to files
#LEVEL ICE
file_name = inpath_table+'SnowModel_'+loc+'_level.csv'
print(file_name)

#calculate means and standard deviations
ts_level_si_m = [ np.mean(x) for x in ts_level_si ]
ts_level_si_std = [ np.std(x) for x in ts_level_si ]

ts_level_it_m = [ np.mean(x) for x in ts_level_it ]
ts_level_it_std = [ np.std(x) for x in ts_level_it ]

#mode
ts_level_it_mo = []
for i in range(0,len(ts_level_it)):
    mo = get_ice_mode(ts_level_it[i],irbins)
    ts_level_it_mo.append(mo)

#print(ts_level_it_m)
#print(ts_level_it_mo)
#exit()

tt = [selection,ts_level_si_m,ts_level_si_std,ts_level_it_m,ts_level_it_std,ts_level_it_mo]
table = list(zip(*tt))

with open(file_name, 'wb') as f:
    #header
    f.write(b'date,snow depth (m),snow depth std (m),ice thickness (m),ice thickness std (m),ice mode (m)\n')
    np.savetxt(f, table, fmt="%s", delimiter=",")

#RUBBLE ICE
file_name = inpath_table+'SnowModel_'+loc+'_rubble.csv'
print(file_name)

#calculate means and standard deviations
ts_rubble_si_m = [ np.mean(x) for x in ts_rubble_si ]
ts_rubble_si_std = [ np.std(x) for x in ts_rubble_si ]

ts_rubble_it_m = [ np.mean(x) for x in ts_rubble_it ]
ts_rubble_it_std = [ np.std(x) for x in ts_rubble_it ]

#mode
ts_rubble_it_mo = []
for i in range(0,len(ts_rubble_it)):
    mo = get_ice_mode(ts_rubble_it[i],irbins)
    ts_rubble_it_mo.append(mo)


tt = [selection,ts_rubble_si_m,ts_rubble_si_std,ts_rubble_it_m,ts_rubble_it_std,ts_rubble_it_mo]
table = list(zip(*tt))

with open(file_name, 'wb') as f:
    #header
    f.write(b'date,snow depth (m),snow depth std (m),ice thickness (m),ice thickness std (m),ice mode (m)\n')
    np.savetxt(f, table, fmt="%s", delimiter=",")


#Sloop
#20191031
#R2 dyn:  0.16536650132568764

#20191107
#R2 dyn:  0.14197341164211152

#20191114
#R2 dyn:  0.44358734589656945

#20191205
#R2 dyn:  0.46842656596873933

#20191226
#R2 dyn:  0.3757705167959082

#20200102
#R2 dyn:  0.4525611817594487

#20200109
#R2 dyn:  0.5033748133427467

#20200116
#R2 dyn:  0.5869684725072333

#20200130
#R2 dyn:  0.626991548590344

#20200206
#R2 dyn:  0.6511211060574689

#20200220
#R2 dyn:  0.5883030088764416

#20200227
#R2 dyn:  0.6367143641630351

#20200305
#R2 dyn:  0.6794766194074568

#20200330
#R2 dyn:  0.6083497335046335

#20200406
#R2 dyn:  0.845961216611923

#20200426
#R2 dyn:  0.292592726344462

#20200507
#R2 dyn:  0.37179857047396847

##############################################
#Sloop
#20191031
#R2 thermo:  0.48794388012415013

#20191107
#R2 thermo:  0.6602568496640939

#20191114
#R2 thermo:  0.30041748975811877

#20191205
#R2 thermo:  0.05609623109951922

#20191226

#20200102

#R2 thermo:  0.15506950129275998

#20200109
#R2 thermo:  0.1777693763351863

#20200116

#20200130
#R2 thermo:  0.020021985900272377

#20200206

#20200220
#R2 thermo:  0.25553871407752027

#20200227
#R2 thermo:  0.2610402589478861

#20200305
#R2 thermo:  0.5017598265954706

#20200330

#R2 thermo:  0.48578808416836494

#20200406
#R2 thermo:  0.775335890626002

#20200426
#R2 thermo:  0.6181196431554159

#20200507
#R2 thermo:  0.7331446427832615
