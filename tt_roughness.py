import numpy as np
from glob import glob
from tt_func import getColumn, running_stats
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

##grid parameters
#stp = '5m'
#stp = '2m_linear'
#stp = '2m_nearest'
#maxdist = 10   #how far away to search in case of nan
##maxdist = 5

#window size for savgol smoothing savgol_filter (must be odd and more than polyorder=3)
polyorder=3
window=231


#location and dates
loc = 'Sloop'
dates = ['20191031','20191107','20191114','20191205',   '20200102','20200109','20200116','20200130','20200206','20200220','20200227','20200305','20200330','20200406','20200426','20200507']
#dates = ['20191031','20191107','20191114','20191205'] #leg1
#dates = ['20191226','20200102','20200109','20200116','20200130','20200206','20200220','20200227'] #leg2
#dates = ['20200305','20200330','20200406','20200426','20200507'] #leg3
dates = ['20191031','20191107','20191114','20191205',   '20200102','20200109','20200116','20200130','20200206','20200220','20200227','20200305','20200330','20200426','20200507']    #best data

dates = ['20191031','20191107','20191114','20191205',   '20191226','20200102','20200109','20200116','20200130','20200206','20200220','20200227','20200305','20200330','20200426','20200507']    #best data

dates = ['20191031','20191107','20191114','20191205',   '20191226','20200102','20200109','20200116','20200130','20200206','20200220','20200227','20200305','20200330','20200406','20200426','20200507']

##early winter
#dates = ['20191031','20191107','20191114']
###deep winter
#dates = ['20191205','20200102','20200109','20200116','20200130','20200206','20200220']
###late winter
#dates = ['20200227','20200305','20200330','20200406','20200426','20200507']

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
inpath_grid = '../data/grids_AGU/'
inpath_weather = '../data/weather/'
outpath = '../plots_AGU/'
outpath = '../plots_gridded/'

step = 2
step = 1
stp = str(step)
method_gem2 = 'nearest'
#method_gem2 = 'linear'
ch_name = '_18kHz'

gridded=True

if gridded==False:
    suff='original'
else:
    suff='gridded_'+str(step)


dt = [ datetime.strptime(x, '%Y%m%d') for x in dates ]
datel = [ datetime.strftime(x, '%Y/%m/%d') for x in dt ]

#what about working with some 'dune footprint' - similar to range in semi-variogram, typically 5-10
dune_range=np.ones_like(dt)*20
dune_range=np.linspace(10, 40, len(dates))              #aprox from semi-varigram
dune_range=[45,45,45,14,20,20,20,20,20,20,20,30,30,30,30,30,30]  #empirically estimated from semi-varigram
#print(dune_range)
#exit()

#Rougness scatter plot
fig4 = plt.figure(figsize=(10,10))
ax = fig4.add_subplot(111)
ax.set_title(title, fontsize=25)
ax.set_xlabel('Roughness (m)', fontsize=20)
ax.set_ylabel('Snow (m)', fontsize=20)
ax.tick_params(axis="x", labelsize=14)
ax.tick_params(axis="y", labelsize=14)
ax.set_xlim(0,1)
ax.set_ylim(0,1)

#Thermodynamics scatter plot
fig1 = plt.figure(figsize=(10,10))
fig1.patch.set_facecolor('0.5')
bx = fig1.add_subplot(111)
bx.set_xlabel('Snow (m)', fontsize=20)
bx.set_title(title, fontsize=25)
bx.set_ylabel('Ice (m)', fontsize=20)
bx.tick_params(axis="x", labelsize=14)
bx.tick_params(axis="y", labelsize=14)
#bx.set_facecolor('0.3')
bx.set_xlim(0,1)
bx.set_ylim(0,2)


std_list=[]
si_list=[]
it_list=[]
dt_list=[]

r2_ts=[]
r2_ts_roughness=[]
r2_ts_roughness2=[]
spacing_ts=[]
total_l=[]
nit_ts=[]

for dd in range(0,len(dates)):
    date = dates[dd]
    dt = datetime.strptime(date, '%Y%m%d')
    dt_list.append(dt)
    print(date)
    
    #outname = 'profile_'+date+'_'+loc+'gridded.png'
        
    if gridded==False:
    
        #choose one 'most perfct' MP track to compare to the others
        fname = glob(inpath_table+'*/magna+gem2-transect-'+date+'*'+loc+'.csv')[0]
        print(fname)
        mxx = getColumn(fname,3, delimiter=',', magnaprobe=False)
        myy = getColumn(fname,4, delimiter=',', magnaprobe=False)
        snod = getColumn(fname,5, delimiter=',', magnaprobe=False)
        it = getColumn(fname,6, delimiter=',', magnaprobe=False)
        mxx = np.array(mxx,dtype=np.float)
        myy = np.array(myy,dtype=np.float)
        si = np.array(snod,dtype=np.float)
        it = np.array(it,dtype=np.float)
    
    else:
        inf = inpath_grid+loc+'_'+stp+'m_'+method_gem2+ch_name+'_track_test.npz'
        inf = inpath_grid+loc+'_'+stp+'m_'+method_gem2+ch_name+'_track1.npz'
        
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
    hist = np.histogram(it,bins=irbins)
    srt = np.argsort(hist[0])                           #indexes that would sort the array
    mm = srt[-1]                                        #same as: np.argmax(hist[0])
    mm1 = np.argmax(hist[0])
    mo = (hist[1][mm] + hist[1][mm+1])/2           #take mean of the bin for the mode value
    print(mo)
    thickice = mo+.3
    
    #get standard deviation of each magnaprobe point
    #based on standard deviation of closest 10 sea ice thickness measurements
    #first/last five measurements are not used
    
    #how many snow depth measurements points should be used
    #decide this based on the MP spacing, so that it is the same total distance for all legs/sampling personel
    
    if gridded==True:
        nit=30                  #very similar results in range 20-40 measurements (m)
        
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
        #if nit < 20:
            #nit=20
            
        dune_range[dd]=int(dune_range[dd]/spacing)
    
    nit_ts.append(nit)
    #nit=30
    
    
    #print(it)
    #print(nit)
    
    ##mean
    #itm = np.convolve(it, np.ones(nit)/nit, mode='valid') #kernel=10
    
    ##print(itm)
    ##print(it.shape)
    ##print(itm.shape)

    ##plt.plot(it,label='thickness')
    ##plt.plot(itm,label='convolve')
    
    

    itm,itv = running_stats(it,nit)
    std = np.sqrt(itv)
    #print(std)
    
    
    
    sim,siv = running_stats(si,nit)
    #print(sim)
    
    
    #first and last few values are zeros!!!
    std_whole = std.copy()
    mask = (sim==0) | np.isnan(sim) | np.isnan(std)
    
    std = np.ma.array(std,mask=mask);std=std.compressed()
    sim = np.ma.array(sim,mask=mask);sim=sim.compressed()
    

    #plot  
    
    
    
    #ax.scatter(std,si,alpha=0.3,c='g')
    ax.scatter(std,sim,alpha=0.1,c=np.array([colors[dd]]))
    
    #r2 estimates
    x = std
    y = sim
    model = np.polyfit(x, y, 1)
    print('coefficients: ', model)
    
    if np.isnan(model[0]):
        r2_ts_roughness.append(0)
    else:
        predict = np.poly1d(model)
        from sklearn.metrics import r2_score
        r2 = r2_score(y, predict(x))
        print('R2: ',r2)
        
        x_lin_reg = np.arange(0, 1.1,.1)
        y_lin_reg = predict(x_lin_reg)
        ax.plot(x_lin_reg, y_lin_reg, c=colors[dd], label=datel[dd])
        
        r2_ts_roughness.append(r2)
        
        
        #estimate some mean values
        level=0
        rubble=0.15
        ridge=0.4
        
        #level ice
        y_pred = predict(level)
        print('level: ',level,y_pred)
        #estimate the volume
        mask = std>rubble
        level_sim = np.ma.array(sim,mask=mask);level_sim=level_sim.compressed()
        vol = np.sum(level_sim)/np.sum(sim)
        print('volume fraction of level ice snow: ',vol)
        level_n = level_sim.shape[0]/sim.shape[0]
        print('volume fraction of level ice: ',level_n)
        
        #rubble
        y_pred = predict(rubble)
        print('rubble: ',rubble,y_pred)
        #estimate the volume
        mask = (std<rubble)
        level_sim = np.ma.array(sim,mask=mask);level_sim=level_sim.compressed()
        vol = np.sum(level_sim)/np.sum(sim)
        print('volume fraction of rubble ice snow: ',vol)
        level_n = level_sim.shape[0]/sim.shape[0]
        print('volume fraction of rubble ice: ',level_n)

        #ridges
        y_pred = predict(ridge)
        print('ridge: ',ridge,y_pred)
        #estimate the volume
        mask = (std<ridge)
        level_sim = np.ma.array(sim,mask=mask);level_sim=level_sim.compressed()
        vol = np.sum(level_sim)/np.sum(sim)
        print('volume fraction of ridge ice snow: ',vol)
        level_n = level_sim.shape[0]/sim.shape[0]
        print('volume fraction of ridge ice: ',level_n)
        
        
        #give snow volume for these classes

        
    
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

    #what about working with some 'dune footprint' - similar to range in semi-variogram, typically 5-10
    
    si,var = running_stats(si,dune_range[dd])   #n has to be divideable by 2
    it,var = running_stats(it,dune_range[dd])
    
    #print(si)
    #exit()
    
    #mask = (std_whole>0.1) | (it>thickice) | (np.isnan(si)) | (si==0) #first and last values in running means are zeros!!!
    #mask = (std_whole>0.09) | (np.isnan(si)) | (si==0)
    #mask = False
    
    #from semivar
    #get distances between points
    dx = mxx[1:]-mxx[:-1]
    dy = myy[1:]-myy[:-1]
    md = np.sqrt(dx**2+dy**2)
    x = np.zeros_like(si)
    x[1:] = np.cumsum(md)
    
    #all level ice between 200 and 700m distance - level ice always thinner than 1m
    #ax.set_title('All level ice - several lines', fontsize=25)
    mask = (x<100) | (x>750)  | (std_whole>0.11) | (si==0) #first and last values in running means are zeros!!!

    

    si_level = np.ma.array(si,mask=mask)
    it_level = np.ma.array(it,mask=mask)

    si_level = si_level.compressed()
    it_level = it_level.compressed()
    
    #print(si_level)
    if len(si_level)==0:
        print('empty series')
        r2_ts.append(0)
        continue


    #plot
    bx.scatter(si_level,it_level,alpha=0.1,c=colors[dd])
    
    x = si_level
    y = it_level
    model = np.polyfit(x, y, 1)
    print('coefficients: ', model)

    predict = np.poly1d(model)
    from sklearn.metrics import r2_score
    r2 = r2_score(y, predict(x))
    print('R2: ',r2)
    r2_ts.append(r2)

    x_lin_reg = np.arange(0, 1.1,.1)
    y_lin_reg = predict(x_lin_reg)
    
    print(x_lin_reg)
    print(y_lin_reg)

    bx.plot(x_lin_reg, y_lin_reg, c=colors[dd], label=datel[dd])
    
    std_list.extend(std_whole)
    si_list.extend(si)
    it_list.extend(it)


#Roughness scatterplot
ax.legend(ncol=3)
fig4.savefig(outpath+'roughness_1'+suff,bbox_inches='tight')
plt.close(fig4)


bx.legend(ncol=3)
fig1.savefig(outpath+'thermo_scatter_1'+suff,bbox_inches='tight')
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
fig2 = plt.figure(figsize=(10,15))
#fig2.patch.set_facecolor('0.5')

start = datetime(2019, 10, 29, 0, 0)
end = datetime(2020, 5, 15, 0, 0)

ax = fig2.add_subplot(311)
ax.set_xlabel('Time', fontsize=20)
#ax.set_title(title+datel[dd], fontsize=25)
ax.set_ylabel('$R^2$', fontsize=20)
ax.tick_params(axis="x", labelsize=14)
ax.tick_params(axis="y", labelsize=14)
#ax.set_facecolor('0.3')
ax.set_xlim(start,end)

ax.plot(dt_list,r2_ts,color='k',ls=':',label='thermodyn. driver')
ax.scatter(dt_list,r2_ts,facecolors=colors,s=70)
ax.plot(dt_list,r2_ts_roughness,color='k',ls='--',label='dyn. driver')
ax.scatter(dt_list,r2_ts_roughness,facecolors=colors,s=70)
#ax.plot(dt_list[1:],r2_ts_roughness2[1:],color='y')
ax.legend(fontsize=15)

#weather
fname = inpath_weather+'weather_Oct-Jul.csv'
print(fname)
date = getColumn(fname,0, delimiter=',', magnaprobe=False)
date = [ datetime.strptime(x, '%Y/%m/%d %H:%M:%S') for x in date ]
wind = getColumn(fname,7, delimiter=',', magnaprobe=False)
wind = np.array(wind,dtype=np.float)
wind = savgol_filter(wind, window, polyorder)

windd = getColumn(fname,6, delimiter=',', magnaprobe=False)
windd = np.array(windd,dtype=np.float)
windd = savgol_filter(windd, window, polyorder)

temp = getColumn(fname,4, delimiter=',', magnaprobe=False)
temp = np.array(temp,dtype=np.float)
temp = savgol_filter(temp, window, polyorder)

bx = fig2.add_subplot(312)
bx.set_xlabel('Time', fontsize=20)
#ax.set_title(title+datel[dd], fontsize=25)
bx.set_ylabel('Wind Speed (m/s)', fontsize=20)
bx.tick_params(axis="x", labelsize=14)
bx.tick_params(axis="y", labelsize=14)
#bx.set_facecolor('0.3')
bx.set_xlim(start,end)


bx.scatter(date,wind,c=windd,cmap=plt.cm.twilight)
bx.legend()

cx = fig2.add_subplot(313)
cx.set_xlabel('Time', fontsize=20)
#ax.set_title(title+datel[dd], fontsize=25)
cx.set_ylabel('Wind direction (deg.)', fontsize=20)
cx.tick_params(axis="x", labelsize=14)
cx.tick_params(axis="y", labelsize=14)
#bx.set_facecolor('0.3')
cx.set_xlim(start,end)

cx.plot(date,temp,c='darkred')

fig2.autofmt_xdate()

fig2.savefig(outpath+'r2_ts1'+suff,bbox_inches='tight')

print(nit_ts)
print(spacing_ts)
print(total_l)
