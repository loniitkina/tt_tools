import numpy as np
from glob import glob
from tt_func import getColumn
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

#prepare time series from gages and snow lines

#snow line: main line (MYI), Baltimore

#gages: close to main line, Baltimore

inpath_s='../data/SHEBA/snow/snowsurv/SNOWSURV/'
inpath_g='../data/SHEBA/mass_balance/gaugedata/'
outpath='../data/SHEBA/snow/'

#snow line time series
#main snow line - MYI (with lots of leads/ridges and one old ridge)
fnames=sorted(glob(inpath_s+'MAINLINE_fixed/ML*.CSV'))
dt_snow_main=[]
m_snow_main=[]
std_snow_main=[]

for fname in fnames:
    #print(fname)
    #get date from fname
    dt = fname.split('ML')[-1].split('.CSV')[0]
    dt_snow_main.append(dt)
    
    #get snow depth
    snod = getColumn(fname,1,skipheader=3)
    snod = np.array(snod,dtype=np.float)/100    #convert to meters
    
    #convert nagative values (melt ponds) to zeroes
    snod = np.where(snod<0,0,snod)
    
    m_snow_main.append(np.mean(snod))
    std_snow_main.append(np.std(snod))

#Baltimore snow line: FYI, ridged in January
fnames=sorted(glob(inpath_s+'BALT_fixed/SBAL*.CSV'))
dt_snow_bal=[]
m_snow_bal=[]
std_snow_bal=[]

for fname in fnames:
    #print(fname)
    #get date from fname
    dt = fname.split('BAL')[-1].split('.CSV')[0]
    dt_snow_bal.append(dt)
    
    #get snow depth
    snod = getColumn(fname,1,skipheader=3)
    snod = np.array(snod,dtype=np.float)/100    #convert to meters
    
    #convert nagative values (melt ponds) to zeroes
    snod = np.where(snod<0,0,snod)
    
    m_snow_bal.append(np.mean(snod))
    std_snow_bal.append(np.std(snod))

dt_snow_main = [ datetime.strptime(x, '%y%m%d') for x in dt_snow_main ]
dt_snow_bal = [ datetime.strptime(x, '%y%m%d') for x in dt_snow_bal ]

#plot snow lines 
plt.errorbar(dt_snow_main,m_snow_main,std_snow_main)
plt.errorbar(dt_snow_bal,m_snow_bal,std_snow_bal)


#ice gauges data
#Baltimore:FYI, includes data between 1-4 m start ice thickness...
fnames=sorted(glob(inpath_g+'*bal_FYI/*BAL*.CSV'))
dt=[]
snow=[]
ice=[]
max_bal=[]

for fname in fnames:
    #print(fname)
    
    date = getColumn(fname,0,skipheader=2)
    snod = getColumn(fname,1,skipheader=2)
    top = getColumn(fname,2,skipheader=2)
    bot = getColumn(fname,3,skipheader=2)
    
    date = [ datetime.strptime(x, '%y%m%d') for x in date ]
    snod = np.array(snod,dtype=np.float)/100
    top = np.array(top,dtype=np.float)/100
    bot = np.array(bot,dtype=np.float)/100
    
    it=top-bot
    #print(it)
    
    #print(date)
    #get mean for 13 May
    for x in range(0,len(date)):
        if date[x]==datetime(1998,5,13):
            max_bal.append(it[x])

    
    #plotting
    plt.plot(date,snod,c='.75')
    
    plt.plot(date,it,c='y')

m_max_bal=np.mean(np.ma.masked_invalid(max_bal))
print(m_max_bal)
plt.plot(datetime(1998,5,15),m_max_bal,'o',c='b')
    

#Main Line
fnames=sorted(glob(inpath_g+'*GAUGE/*ML*.CSV'))
dt=[]
snow=[]
ice=[]
max_ml=[]

for fname in fnames:
    #print(fname)
    
    date = getColumn(fname,0,skipheader=2)
    snod = getColumn(fname,1,skipheader=2)
    top = getColumn(fname,2,skipheader=2)
    bot = getColumn(fname,3,skipheader=2)
    
    date = [ datetime.strptime(x, '%y%m%d') for x in date ]
    snod = np.array(snod,dtype=np.float)/100
    top = np.array(top,dtype=np.float)/100
    bot = np.array(bot,dtype=np.float)/100
    
    it=top-bot
    #print(date)
    #print(it)
    
    #get mean for 15 May
    for x in range(0,len(date)):
        if date[x]==datetime(1998,5,15):
            max_ml.append(it[x])
            
    
    
    #plotting
    plt.plot(date,snod,c='c')
    
    plt.plot(date,it,c='g')
    
m_max_ml=np.mean(np.ma.masked_invalid(max_ml))
print(m_max_ml)
plt.plot(datetime(1998,5,15),m_max_ml,'o',c='r')


#plot gauges
plt.show()

#save main snow line
#time series text file exports
file_main=outpath+'ts_sheba_snow_main.csv'
tt = [dt_snow_main,m_snow_main,std_snow_main]
table = list(zip(*tt))

print(file_main)
with open(file_main, 'wb') as f:
    #header
    f.write(b'Date, snow depth mean, snow depth SD\n')
    np.savetxt(f, table, fmt="%s", delimiter=",")

    
#FYI level ice span between 1-1.5m
#SYI/MYI level ice spans between 1.5-2.5m
