import numpy as np
from glob import glob
from tt_func import getColumn
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

#compare all time series written by tt_pdf_plot: Nloop, Sloop, snow1, runway (+maybe some special transect)

#also bring in other historical data from e.g. climatology (CS-2), SHEBA, N-ICE, Damocles/Tara drift
#just transect data, no buoys etc...

#note: most of these transects are actually MYI or SYI


fig1 = plt.figure(figsize=(20,15))
cx = fig1.add_subplot(211)
#cx.set_title(title, fontsize=25)
cx.set_ylabel('Snow depth (m)', fontsize=20)
cx.tick_params(axis="x", labelsize=14)
cx.tick_params(axis="y", labelsize=14)
cx.set_ylim(0,.85)

dx = fig1.add_subplot(212)
dx.set_ylabel('Ice thickness (m)', fontsize=20)
dx.tick_params(axis="x", labelsize=14)
dx.tick_params(axis="y", labelsize=14)
dx.set_ylim(0,6)



dt_start= datetime(2019,8,1)



#MOSAiC
locs=['Sloop','Nloop','runway','snow1']
locs = ['Nloop','Sloop','transect','ridge*','snow1','runway','albedoRBB','albedoLD','albedoK','kuka','ARIEL','special']

#colors matching the map
cols = ['salmon','purple','orange','limegreen','gold','deeppink','hotpink','cornflowerblue','m','k','r','c']


outpath='../plots_AGU/'
outname='ts_comp.png'

inpath_mosaic='../data/MCS/MP/'
i=0
for loc in locs:
    fname=inpath_mosaic+'ts_'+loc+'_2m_gridded.csv'
    try:
        dt1= getColumn(fname,0)
        m_snow= getColumn(fname,1)
        std_snow= getColumn(fname,2)
        m_ice= getColumn(fname,3)
        std_ice= getColumn(fname,4)
        mo_ice= getColumn(fname,5)
        dt = [ datetime.strptime(x, '%Y%m%d') for x in dt1 ]
        m_snow = np.array(m_snow,dtype=np.float)
        std_snow = np.array(std_snow,dtype=np.float)
        m_ice = np.array(m_ice,dtype=np.float)
        std_ice = np.array(std_ice,dtype=np.float)
        mo_ice = np.array(mo_ice,dtype=np.float)
        
        #flag bad ice thickness data
        if loc=='Sloop' or loc=='Nloop':
            for x in range(0,len(dt1)):
                if dt1[x]=='20200206':
                    m_ice[x]=np.nan
        #if loc=='Nloop':
            #for x in range(0,len(dt1)):
                #if dt1[x]=='20191031' or dt1[x]=='20191114':
                    #m_ice[x]=np.nan    

        
        #time axis
        if loc=='special' or loc=='kuka' or loc=='ARIEL' or loc=='albedoK':
            #get leg 5 as start of MOSAiC
            dt1 = [ x-timedelta(days=366) for x in dt if x > datetime(2020,8,1)  ]
            dt[-1*int(len(dt1)):] = dt1   #push those dates forward

        dt_diff = [ (x-dt_start).days for x in dt ]

        #plotting
        #snow
        #shift Sloop by 1 day so it not overlayed completly by Nloop
        if loc=='Sloop':
            dt_diff = [ x+1 for x in dt_diff ]
            cx.errorbar(dt_diff,m_snow, std_snow, linestyle='None', marker='o',c=cols[i],label=loc,alpha=.5)
        else:
            cx.errorbar(dt_diff,m_snow, std_snow, linestyle='None', marker='o',c=cols[i],label=loc,alpha=.5)
        
        
        #ice
        dx.errorbar(dt_diff,m_ice, std_ice, linestyle='None', marker='o',c=cols[i],alpha=.5)
        if loc=='Sloop':
            dx.plot(dt_diff,mo_ice,'s',ms=5,c='.5',label='mode')
            #dx.plot(dt_diff,mo_ice,'.',ms=10,c='b',label='Sloop-type mode')
        #elif loc=='Nloop':
            #dx.plot(dt_diff,mo_ice,'s',ms=10,c='.5')
            #dx.plot(dt_diff,mo_ice,'.',ms=10,c='r',label='Nloop-type mode')
            
        #elif loc=='albedoK':
            #dx.plot(dt_diff,mo_ice,'s',ms=10,c='.5')
            #dx.plot(dt_diff,mo_ice,'.',ms=10,c='r')
        else:
            dx.plot(dt_diff,mo_ice,'s',ms=5,c='.5')
        i=i+1
    except:
        i=i+1
        continue

#N-ICE2015 data
inpath_nice='../data/N-ICE/'
fname=inpath_nice+'ts_nice_transitions.csv' #manually added dummy transitions between floes (zeros)
dt_nice= getColumn(fname,0)
type_nice= getColumn(fname,1)
m_snow_nice= getColumn(fname,2)
std_snow_nice= getColumn(fname,3)
m_ice_nice= getColumn(fname,4)
std_ice_nice= getColumn(fname,5)
mo_ice_nice= getColumn(fname,6)
dt_nice = [ datetime.strptime(x, '%Y-%m-%d %H:%M:%S') for x in dt_nice ]
m_snow_nice = np.array(m_snow_nice,dtype=np.float)
std_snow_nice = np.array(std_snow_nice,dtype=np.float)
m_ice_nice = np.array(m_ice_nice,dtype=np.float)
std_ice_nice = np.array(std_ice_nice,dtype=np.float)
mo_ice_nice = np.array(mo_ice_nice,dtype=np.float)

#subtract snow from total thickness to get ice thickness
m_ice_nice = m_ice_nice-m_snow_nice
mo_ice_nice = mo_ice_nice-m_snow_nice

#filter transect types
#print(type_nice)
#only keep repeated transects
type_maskM=[]
type_maskF=[]
for x in type_nice:
    if x=='tM' or x=='t' or x=='t1':
        type_maskM.append(0)
    else:
        type_maskM.append(1)
        
    if x=='tF' or x=='t' or x=='t1':
        type_maskF.append(0)
    else:
        type_maskF.append(1)
        
#print(type_maskM)
#print(type_maskF)

dt_niceM = np.ma.array(dt_nice,mask=type_maskM).compressed()
m_snow_niceM = np.ma.array(m_snow_nice,mask=type_maskM).compressed()
std_snow_niceM = np.ma.array(std_snow_nice,mask=type_maskM).compressed()
m_ice_niceM = np.ma.array(m_ice_nice,mask=type_maskM).compressed()
std_ice_niceM = np.ma.array(std_ice_nice,mask=type_maskM).compressed()
mo_ice_niceM = np.ma.array(mo_ice_nice,mask=type_maskM).compressed()

dt_niceF = np.ma.array(dt_nice,mask=type_maskF).compressed()
m_snow_niceF = np.ma.array(m_snow_nice,mask=type_maskF).compressed()
std_snow_niceF = np.ma.array(std_snow_nice,mask=type_maskF).compressed()
m_ice_niceF = np.ma.array(m_ice_nice,mask=type_maskF).compressed()
std_ice_niceF = np.ma.array(std_ice_nice,mask=type_maskF).compressed()
mo_ice_niceF = np.ma.array(mo_ice_nice,mask=type_maskF).compressed()

#mask zeros to indicate transitions between legs
m_snow_niceF = np.ma.array(m_snow_niceF,mask=m_snow_niceF==0)
m_snow_niceM = np.ma.array(m_snow_niceM,mask=m_snow_niceM==0)
m_ice_niceF = np.ma.array(m_ice_niceF,mask=m_ice_niceF==0)
m_ice_niceM = np.ma.array(m_ice_niceM,mask=m_ice_niceM==0)
mo_ice_niceF = np.ma.array(mo_ice_niceF,mask=mo_ice_niceF==0)
mo_ice_niceM = np.ma.array(mo_ice_niceM,mask=mo_ice_niceM==0)

#SHEBA 1997/98 data
#Main snow line: SYI, but with lots of leads!
inpath_sheba='../data/SHEBA/snow/'
fname=inpath_sheba+'ts_sheba_snow_main.csv'
dt_sheba= getColumn(fname,0)
m_snow_sheba= getColumn(fname,1)
std_snow_sheba= getColumn(fname,2)
dt_sheba = [ datetime.strptime(x, '%Y-%m-%d %H:%M:%S') for x in dt_sheba ]
m_snow_sheba = np.array(m_snow_sheba,dtype=np.float)
std_snow_sheba = np.array(std_snow_sheba,dtype=np.float)



#CLIMATOLOGY/CS-2
inpath_cs2 = '../data/CS2/'
fname = inpath_cs2+'l2p-extract-sit-0050km-20191001-20200430.csv'
dt_cs2= getColumn(fname,0, delimiter=',')
m_cs2= getColumn(fname,4, delimiter=',')
dt_cs2 = [ datetime.strptime(x, '%Y-%m-%d') for x in dt_cs2 ]
m_cs2 = np.where(m_cs2=='','0',m_cs2)
m_cs2[m_cs2=='']='0'    #replace empty strings with values
m_cs2 = np.array(m_cs2,dtype=np.float)
m_cs2 = np.ma.array(m_cs2,mask=m_cs2==0)

fname = inpath_cs2+'l2p-extract-sd-0050km-20191001-20200430.csv'
m_cs2sd= getColumn(fname,4, delimiter=',')
m_cs2sd = np.where(m_cs2sd=='','0',m_cs2sd)
m_cs2sd[m_cs2sd=='']='0'    #replace empty strings with values
m_cs2sd = np.array(m_cs2sd,dtype=np.float)
m_cs2sd = np.ma.array(m_cs2sd,mask=m_cs2sd==0)

#Warren99 climatology
from netCDF4 import Dataset
inpath_w99='../data/W99/'
fnames = sorted(glob(inpath_w99+'*.nc'))
f = Dataset(fnames[0])
lats = f.variables['latitude'][:]
lons = f.variables['longitude'][:]

#instead of MOSAiC track
window = (lats>75)*(lats<89)*(lons<150)*(lons>0)

m_w99=[]
dates_w99= ['20200115','20200215','20200315','20200415','20200515','20200615','20200715','20200815','20190915','20191015','20191115','20191215']
dt_w99 = [ datetime.strptime(x, '%Y%m%d') for x in dates_w99 ]

#IAV: interannual variablity - one value per month - copied straight from the paper
#IAV: standard deviation of the annomalies of individual month from multiyear average for that month.

iav_w99=np.array([4.6,5.5,6.2,6.1,6.3,8.1,6.7,3.3,3.8,4.0,4.3,4.8])/100 #convert from cm to m.

for fname in fnames:
    #print(fname)
    f = Dataset(fname)
    snod = f.variables['snow_depth'][:]
    f.close()
    
    snod_w = np.ma.array(snod,mask=window).compressed()
    snod_m = np.mean(np.ma.masked_invalid(snod_w))
    #print(snod_m)
    
    m_w99.append(snod_m)

#plot sheba
dt_sheba = [ x+timedelta(days=365*22) for x in dt_sheba  ]
dt_diff_sheba = [ (x-dt_start).days for x in dt_sheba ]

cx.plot(dt_diff_sheba,m_snow_sheba,c='.75')
sigma_sM = cx.fill_between(dt_diff_sheba,m_snow_sheba-std_snow_sheba,m_snow_sheba+std_snow_sheba,color='.9',label='SHEBA')


#plot N-ICE2015
dt_niceM = [ x+timedelta(days=366*5) for x in dt_niceM  ]
dt_diff_niceM = [ (x-dt_start).days for x in dt_niceM ]
#cx.errorbar(dt_diff_niceM,m_snow_niceM,std_snow_niceM,linestyle='None',marker='.',ms=10,label='N-ICE2015 M',c='.75')
#dx.errorbar(dt_diff_niceM,m_ice_niceM,std_ice_niceM,linestyle='None',marker='.',ms=10,c='.75')
dx.plot(dt_diff_niceM,mo_ice_niceM,'s',c='.85')

dt_niceF = [ x+timedelta(days=366*5) for x in dt_niceF  ]
dt_diff_niceF = [ (x-dt_start).days for x in dt_niceF ]
#cx.errorbar(dt_diff_niceF,m_snow_niceF,std_snow_niceF,linestyle='None',marker='.',ms=10,label='N-ICE2015 F',c='.85')
#dx.errorbar(dt_diff_niceF,m_ice_niceF,std_ice_niceF,linestyle='None',marker='.',ms=10,c='.85')
dx.plot(dt_diff_niceF,mo_ice_niceF,'s',c='.85')


cx.plot(dt_diff_niceM,m_snow_niceM,c='.85')
sigma_sM = cx.fill_between(dt_diff_niceM,m_snow_niceM-std_snow_niceM,m_snow_niceM+std_snow_niceM,color='.95',label='N-ICE2015')
cx.plot(dt_diff_niceF,m_snow_niceF,c='.85')
sigma_sF = cx.fill_between(dt_diff_niceF,m_snow_niceF-std_snow_niceF,m_snow_niceF+std_snow_niceF,color='.95')

dx.plot(dt_diff_niceM,m_ice_niceM,c='.85')
sigma_sM = dx.fill_between(dt_diff_niceM,m_ice_niceM-std_ice_niceM,m_ice_niceM+std_ice_niceM,color='.95')
dx.plot(dt_diff_niceF,m_ice_niceF,c='.85')
sigma_sF = dx.fill_between(dt_diff_niceF,m_ice_niceF-std_ice_niceF,m_ice_niceF+std_ice_niceF,color='.95')

#plot climatology
dt_diff_w99 = [ (x-dt_start).days for x in dt_w99 ]
#cx.plot(dt_diff_w99,m_w99,'*',ms=10,label='W99 climatology',c='darkred')
cx.errorbar(dt_diff_w99,m_w99,iav_w99,linestyle='None',marker='*',ms=10,label='W99 climatology',c='darkred')

##plot CS-2
#dt_diff_cs2 = [ (x-dt_start).days for x in dt_cs2 ]
#cx.plot(dt_diff_cs2,m_cs2sd,'.',label='CS-2 snow',c='.75')
#dx.plot(dt_diff_cs2,m_cs2,'.',label='CS-2 mean',c='.75')


#and a dirty trick for the X axis    
dates_m = ['20190901','20191001','20191101','20191201','20200101','20200201','20200301','20200401','20200501','20200601','20200701','20200801']
dt_m = [ datetime.strptime(x, '%Y%m%d') for x in dates_m ]
dt_diff_m = [ (x-dt_start).days for x in dt_m ]
plt.xticks(dt_diff_m, ['1 Sep','1 Oct','1 Nov','1 Dec','1 Jan','1 Feb','1 Mar','1 Apr','1 May','1 Jun','1 Jul','1 Aug'])


cx.legend(fontsize=14,fancybox=True,framealpha=.9,ncol=3,loc='upper left')
dx.legend(fontsize=14,fancybox=True,framealpha=.9,ncol=1,loc='upper left')

cx.set_xticks(dt_diff_m)
dx.set_xticks(dt_diff_m)
fig1.autofmt_xdate()

cx.set_xlim(20,366)
dx.set_xlim(20,366)

fig1.savefig(outpath+outname,bbox_inches='tight')
plt.close(fig1)
