import numpy as np
from glob import glob
from tt_func import getColumn
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

##early winter
#dates = ['20191031','20191107','20191114']
###deep winter
#dates = ['20191205','20200102','20200109','20200116','20200130','20200206','20200220']
###late winter
#dates = ['20200227','20200305','20200330','20200406','20200426','20200507']

title='Southeren transect loop '

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
#colors = plt.cm.rainbow(np.linspace(0, 1, len(dates)))
colors = plt.cm.Blues(np.linspace(0, 1, len(dates)))

if len(dates) == 1:
    colors = ['.1','.5']
    

inpath_table = '../data/MCS/MP/'
inpath_weather = '../data/weather/'
outpath = '../plots_AGU/'


std_list=[]
si_list=[]
it_list=[]
dt_list=[]

r2_ts=[]
spacing_ts=[]
nit_ts=[]

for dd in range(0,len(dates)):
    date = dates[dd]
    dt = datetime.strptime(date, '%Y%m%d')
    dt_list.append(dt)
    print(date)
    
    outname = 'profile_'+date+'_'+loc+'gridded.png'
    
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
    
    #get sea ice thickness mode
    irbins = np.arange(0,2,.06)
    hist = np.histogram(it,bins=irbins)
    srt = np.argsort(hist[0])                           #indexes that would sort the array
    mm = srt[-1]                                        #same as: np.argmax(hist[0])
    mm1 = np.argmax(hist[0])
    mo = (hist[1][mm] + hist[1][mm+1])/2           #take mean of the bin for the mode value
    print(mo)
    thickice = mo+.2
    
    #get standard deviation of each magnaprobe point
    #based on standard deviation of closest 10 sea ice thickness measurements
    #first/last five measurements are not used
    
    #how many snow depth measurements points should be used
    #decide this based on the MP spacing, so that it is the same total distance for all legs/sampling personel
    
    dx = mxx[1:]-mxx[:-1]
    dy = myy[1:]-myy[:-1]
    print('MP measurement spacing:')
    spacing = np.mean(np.sqrt(dx**2+dy**2))
    print(spacing)
    spacing_ts.append(spacing)
    
    nit = int(30/spacing)   #take 50m distance as a starting point
    print(nit)
    if nit < 20:
        nit=20
    
    nit_ts.append(nit)
    #nit=30
    
    
    
    #mean
    itm = np.convolve(it, np.ones(nit)/nit, mode='valid') #kernel=10
    
    #print(itm)
    #print(it.shape)
    #print(itm.shape)

    #plt.plot(it,label='thickness')
    #plt.plot(itm,label='convolve')
    
    
    def running_stats(x, n):            #n has to be dividable by 2!
        sum1 = np.zeros_like(x)
        sum2 = np.zeros_like(x)
        x2 = x**2
        n2 = int(n/2)
        
        for i in range(n2,len(x)-n2):
            #print(i)
            #print(len(x[i-n2:i+n2]))
            #print(x[i-n2:i+n2])
            #print(np.sum(x[i-n2:i+n2]))
            sum1[i] = np.sum(x[i-n2:i+n2])
            sum2[i] = np.sum(x2[i-n2:i+n2])
            
            #print(sum1[i])
            #print(sum2[i])
        #exit()
        
        mean = sum1/n
        var = (sum2/n - mean**2)
        return (mean,var)

    itm,itv = running_stats(it,nit)
    #print(itm)
    #print(it.shape)
    #print(itm.shape)
    
    #plt.plot(itm,label='sum')
    #plt.plot(itv,label='var')

    
    #calculating variance in two-pass:
    def running_var(x,mu,n):
        
        sum2 = np.zeros_like(x)
        
        n2 = int(n/2)
        
        for i in range(n2,len(x)-n2):
            
            #print(i)
            #print(x[i])
            #print(x[i-n2:i+n2])
            #print(x[i-n2:i+n2]-mu[i-n2:i+n2])
            #print((x[i-n2:i+n2]-mu[i-n2:i+n2])**2)
            
            sum2[i] = np.sum((x[i-n2:i+n2]-mu[i-n2:i+n2])**2)
            
            #print(sum2[i])
            
        #exit()
        
        var = sum2/n
        
        return (var)
        
    itv2 = running_var(it,itm,nit)
    
    #plt.plot(itv2,label='var2')
    
    #plt.plot(np.ones_like(it)*0.1)
    
    #plt.legend()
    #plt.show()

    std = np.sqrt(itv)

    #plot
    fig4 = plt.figure(figsize=(10,10))
    
    ax = fig4.add_subplot(111)
    ax.set_xlabel('Roughness (m)', fontsize=20)
    ax.set_ylabel('Snow (m)', fontsize=20)
    ax.tick_params(axis="x", labelsize=14)
    ax.tick_params(axis="y", labelsize=14)
    
    ax.scatter(std,si,alpha=0.3)
    
    fig4.savefig(outpath+'roughness_'+date)
                 
    
    #thermodynamics plot
    #take all the roughness < 0.1 and plot thickness against snow depth
    #thickice margin helps to mask the outliers - needs to be replaced by mode???
    mask = (std>0.1) | (it>thickice)

    si_level = np.ma.array(si,mask=mask)
    it_level = np.ma.array(it,mask=mask)

    si_level = si_level.compressed()
    it_level = it_level.compressed()


    #plot
    fig1 = plt.figure(figsize=(10,10))
    fig1.patch.set_facecolor('0.5')

    ax = fig1.add_subplot(111)
    ax.set_xlabel('Snow (m)', fontsize=20)
    #ax.set_title(title+datel[dd], fontsize=25)
    ax.set_ylabel('Ice (m)', fontsize=20)
    ax.tick_params(axis="x", labelsize=14)
    ax.tick_params(axis="y", labelsize=14)
    #ax.set_facecolor('0.3')

    ax.scatter(si_level,it_level,alpha=0.1)
    
    x = si_level
    y = it_level
    model = np.polyfit(x, y, 1)
    print('coefficients: ', model)

    predict = np.poly1d(model)
    from sklearn.metrics import r2_score
    r2 = r2_score(y, predict(x))
    print('R2: ',r2)
    r2_ts.append(r2)

    x_lin_reg = np.arange(0, 1,.1)
    y_lin_reg = predict(x_lin_reg)

    ax.plot(x_lin_reg, y_lin_reg, c = 'r')
    
    fig1.savefig(outpath+'thermo_scatter_'+date)
    
    std_list.extend(std)
    si_list.extend(si)
    it_list.extend(it)

std_list = np.array(std_list)

mask = (std_list==0) | np.isnan(std_list)

std_list = np.ma.array(std_list,mask=mask)
si_list = np.ma.array(si_list,mask=mask)
it_list = np.ma.array(it_list,mask=mask)

std_list = std_list.compressed().tolist()
si_list = si_list.compressed().tolist()
it_list = it_list.compressed()

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

fig3 = plt.figure(figsize=(10,10))
ax = fig3.add_subplot(111)
ax.set_xlabel('Roughness', fontsize=20)
#ax.set_title(title+datel[dd], fontsize=25)
ax.set_ylabel('Snow', fontsize=20)
ax.tick_params(axis="x", labelsize=14)


ax.scatter(x, y,alpha=0.01)
ax.plot(x_lin_reg, y_lin_reg, c = 'r')
fig3.savefig(outpath+'roughness_all')


#time series of thermodynamics r2
fig2 = plt.figure(figsize=(10,10))
#fig2.patch.set_facecolor('0.5')

start = datetime(2019, 10, 1, 0, 0)
end = datetime(2020, 6, 1, 0, 0)

ax = fig2.add_subplot(211)
ax.set_xlabel('Time', fontsize=20)
#ax.set_title(title+datel[dd], fontsize=25)
ax.set_ylabel('R2', fontsize=20)
ax.tick_params(axis="x", labelsize=14)
ax.tick_params(axis="y", labelsize=14)
#ax.set_facecolor('0.3')
ax.set_xlim(start,end)

ax.plot(dt_list,r2_ts)

#weather
fname = inpath_weather+'weather_Oct-Jul.csv'
print(fname)
date = getColumn(fname,0, delimiter=',', magnaprobe=False)
date = [ datetime.strptime(x, '%Y/%m/%d %H:%M:%S') for x in date ]
wind = getColumn(fname,7, delimiter=',', magnaprobe=False)
wind = np.array(wind,dtype=np.float)
wind = savgol_filter(wind, window, polyorder)

bx = fig2.add_subplot(212)
bx.set_xlabel('Time', fontsize=20)
#ax.set_title(title+datel[dd], fontsize=25)
bx.set_ylabel('Wind Speed (m/s)', fontsize=20)
bx.tick_params(axis="x", labelsize=14)
bx.tick_params(axis="y", labelsize=14)
#bx.set_facecolor('0.3')
bx.set_xlim(start,end)

bx.plot(date,wind)


fig2.autofmt_xdate()

fig2.savefig(outpath+'r2_ts')

print(nit_ts)
print(spacing_ts)
