import numpy as np
from glob import glob
from tt_func import getColumn
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

#get the N-ICE transect data, make PDFs of snow depth and total ice thickness
#get mean/mode ice thickness by subtracting mean snow depth from it

#make time series for fF, tS, tmix, i (special)

#time span: 15/1/2015 to 21/6

inpath_mp='../data/N-ICE/N-ICE2015_MP_v1/edited/'
inpath_em='../data/N-ICE/N-ICE2015_EM31_v1/edited/'

outpath='../data/N-ICE/'
file_ts=outpath+'ts_nice.csv'

##fix empty line problem
##some manual cleaning will still be necessary...
#fnames=sorted(glob(inpath_mp+'*.txt'))
#import csv
#for fname in fnames:
    #outname=fname.split('.txt')[0]+'.csv'
    #with open(fname) as in_file:
        #with open(outname, 'w') as out_file:
            #writer = csv.writer(out_file)
            #for row in csv.reader(in_file):
                #if row:
                    #writer.writerow(row)



#snow time series
dt_snow=[]
m_snow=[]
std_snow=[]
ttype=[]    #transect type

fnames=sorted(glob(inpath_mp+'*.csv'))

for fname in fnames:
    print(fname)
    date=fname.split('/')[-1].split('_MP')[0]
    print(date)
    dt_snow.append(date)
    
    tt=fname.split('_')[-1].split('.')[0]
    ttype.append(tt)

    snod=getColumn(fname,2,delimiter=' ')
    #print(snod)
    snod = np.array(snod,dtype=np.float)/100    #convert to meters
    #print(snod)
    m = np.mean(np.ma.masked_invalid(snod))
    std = np.std(np.ma.masked_invalid(snod))
    print(m)
    m_snow.append(m)
    std_snow.append(std)
    
    
#print(ttype)    

##fix empty line problem
##some manual cleaning will still be necessary...
#fnames=sorted(glob(inpath_em+'*.txt'))
#import csv
#for fname in fnames:
    #outname=fname.split('.txt')[0]+'.csv'
    #with open(fname) as in_file:
        #with open(outname, 'w') as out_file:
            #writer = csv.writer(out_file)
            #for row in csv.reader(in_file):
                #if row:
                    #writer.writerow(row)
#exit()


#ice time series
dt_ice=[]
m_ice=[]
std_ice=[]
mo_ice=[]
irbins = np.arange(0,3,.06)
ttype_ice=[]    #transect type

fnames=sorted(glob(inpath_em+'*.csv'))

for fname in fnames:
    print(fname)
    date=fname.split('/')[-1].split('L')[0].split('_')[0]
    print(date)
    dt_ice.append(date)
    
    tt=fname.split('_')[-1].split('.csv')[0]
    ttype_ice.append(tt)

    it=getColumn(fname,2,delimiter=',')
    #print(it)
    it = np.array(it,dtype=np.float)
    #print(it)
    m = np.mean(np.ma.masked_invalid(it))
    std = np.std(np.ma.masked_invalid(it))
    print(m)
    
    #find mode
    it_pos = np.ma.masked_invalid(it)
    hist = np.histogram(it_pos,bins=irbins)
    srt = np.argsort(hist[0])                           #indexes that would sort the array
    mm = srt[-1]                                        #same as: np.argmax(hist[0])
    mm1 = np.argmax(hist[0])
    mo = (hist[1][mm] + hist[1][mm+1])/2           #take mean of the bin for the mode value
    print(mo)
    
    m_ice.append(m)
    std_ice.append(std)
    mo_ice.append(mo)



#match these dates - if we want to subtract snow mean from ice!
#print(dt_snow)
#print(dt_ice)
#print(ttype)
#print(ttype_ice)

dt_snow = [ datetime.strptime(x, '%Y_%m_%d') for x in dt_snow ]
dt_ice = [ datetime.strptime(x, '%Y%m%d') for x in dt_ice ]

dt_combi=[]
m_snow_combi=[]
std_snow_combi=[]
m_ice_combi=[]
mo_ice_combi=[]
std_ice_combi=[]
ttype_combi=[]

#select transects with matching date and transect type!
for i in range(0,len(dt_snow)):
    #print(dt_snow[i])
    #print(ttype[i])
    for m in range(0,len(dt_ice)):
        if dt_snow[i]==dt_ice[m] and ttype[i]==ttype_ice[m]:
            print('match',dt_ice[m],ttype_ice[m])
            dt_combi.append(dt_snow[i])
            ttype_combi.append(ttype[i])
            m_snow_combi.append(m_snow[i])
            std_snow_combi.append(std_snow[i])
            m_ice_combi.append(m_ice[m])
            std_ice_combi.append(std_ice[m])           
            mo_ice_combi.append(mo_ice[m])


#print(len(std_snow_combi))
#print(len(m_snow_combi))
#print(len(dt_combi))

plt.errorbar(dt_combi,m_snow_combi,std_snow_combi, linestyle='None', marker='o')
plt.errorbar(dt_combi,m_ice_combi,std_ice_combi, linestyle='None', marker='o',label='mean')
plt.plot(dt_combi,mo_ice_combi,'o',label='mode')
plt.legend()
plt.show()


#time series text file exports
tt = [dt_combi,ttype_combi,m_snow_combi,std_snow_combi,m_ice_combi,std_ice_combi,mo_ice_combi]
table = list(zip(*tt))

print(file_ts)
with open(file_ts, 'wb') as f:
    #header
    f.write(b'Date, transect type, snow depth mean, snow depth SD, total thickness mean, total thickness SD, total thickness mode\n')
    np.savetxt(f, table, fmt="%s", delimiter=",")
