import numpy as np
from glob import glob
import csv
import re
from tt_func import getColumn
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from matplotlib.dates import MonthLocator, DateFormatter
import locale


#Plot overview of all snow depth and ice thickness observations (for all transects)

#Nloop, Sloop, Runway
#level and deformed

#WARNING: Nloop and Sloop inclde some leads from mid April and May on, so the level ice snow depth is biased low.


inpath = '../data/MCS/MP/SnowModel_calval/'
inpath_coring = '../data/coring_dark_site_Evgenii/'
outpath = '../plots_sm/'
locs = ['Nloop','Sloop','runway']

types = ['level','deformed']

colors = plt.cm.rainbow(np.linspace(0, 1, len(locs)*len(types)))

fig1 = plt.figure(figsize=(15,15))
ax = fig1.add_subplot(211)
ax.set_ylabel('Mean snow depth (m)',fontsize=20)

bx = fig1.add_subplot(212)
bx.set_ylabel('Ice thickness mode (m)',fontsize=20)

i=0
for loc in locs:
    print(loc)
    for tt in types:
        print(tt)

        fname = glob(inpath+'SnowModel_'+loc+'_'+tt+'.csv')[0]
        print(fname)

        #b'date,snow depth (m),snow depth std (m),ice thickness (m),ice thickness std (m),ice mode (m)\n'

        dates = getColumn(fname,0)
        dt = [ datetime.strptime(x, '%Y%m%d') for x in dates ]
        snod = getColumn(fname,1);snod = np.array(snod,dtype=np.float)
        snod_std = getColumn(fname,2);snod_std = np.array(snod_std,dtype=np.float)
        it = getColumn(fname,5);it = np.array(it,dtype=np.float)
        
        #Sloop and Nloop are sampled on same days - as a bit of a shift to avoid overlay
        if loc=='Sloop':
            dt = [ x+timedelta(hours=12) for x in dt ]

        ##add dark site coring data
        #if loc=='runway' and tt=='level':
            #fn='FYI_snow_clean.csv'
            #fname = glob(inpath_coring+fn)[0]
            
            ##only take data until end of leg3 (pre-melt)
            #dates = getColumn(fname,10)[:-5]
            #dt_c = [ datetime.strptime(x, '%m/%d/%Y %H:%M') for x in dates ]
            #snod_c = getColumn(fname,1)[:-5];snod_c = np.array(snod_c,dtype=np.float)/100
            #snod_c_std = np.zeros_like(snod_c)  #no standard deviation available
            #it_c = getColumn(fname,13)[:-5];it_c = np.array(it_c,dtype=np.float)/100
            
            #dt.extend(dt_c)
            #snod=np.append(snod,snod_c)
            #snod_std=np.append(snod_std,snod_c_std)
            #it=np.append(it,it_c)
            
        #if loc=='Nloop' and tt=='level':
            #fn='SYI_snow_clean.csv'
            #fname = glob(inpath_coring+fn)[0]
            
            #dates = getColumn(fname,10)[:-4]
            #dt_c = [ datetime.strptime(x, '%m/%d/%Y %H:%M') for x in dates ]
            #snod_c = getColumn(fname,1)[:-4];snod_c = np.array(snod_c,dtype=np.float)/100
            #snod_c_std = np.zeros_like(snod_c)  #no standard deviation available
            #it_c = getColumn(fname,13)[:-4];it_c = np.array(it_c,dtype=np.float)/100
            
            #dt.extend(dt_c)
            #snod=np.append(snod,snod_c)
            #snod_std=np.append(snod_std,snod_c_std)
            #it=np.append(it,it_c)
        
        ##add same start as level ice and same end as deformed Sloop
        #if loc=='runway' and tt=='deformed':
            #dt.append(datetime(2019,11,1))
            #snod=np.append(snod,.1)
            #snod_std=np.append(snod_std,0)
            #it=np.append(it,.4)
            
            #dt.append(datetime(2020,5,7))
            #snod=np.append(snod,.32)
            #snod_std=np.append(snod_std,0)
            #it=np.append(it,2)
            
            
        
        #there are nans in coring snow data
        snod=np.ma.masked_invalid(snod)
        #fit the curve - snow
        x = mdates.date2num(np.ma.array(dt,mask=snod.mask).compressed()) #convert time tuples to numbers
        y = snod.compressed()
        
        print(len(x))
        print(len(y))
        
        model = np.polyfit(x, y, 2) #decide here the curve-order
        predict = np.poly1d(model)

        xmodel = np.arange(min(x),max(x),1) #convert numbers to dates for plotting
        dd = mdates.num2date(xmodel)
        ymodel = predict(xmodel)

        if tt=='level':
            ls='-'
        else:
            ls=':'
            tt='def.'
            
            #move by a short time step to avoid overlay
            dt = [ x+timedelta(hours=12) for x in dt ]
            
        #ax.plot(dd, ymodel,ls=ls,alpha=.9,lw=3,label=loc+' '+tt,c=colors[i])
        ax.errorbar(dt,snod,snod_std,linestyle='None',c=colors[i], marker='x',label=loc+' '+tt)

        #fit the curve - ice
        x = mdates.date2num(dt)
        y = it
        model = np.polyfit(x, y, 2) #decide here the curve-order
        predict = np.poly1d(model)

        ymodel = predict(xmodel)


        if tt=='level':
        #plot only modes for level ice
            bx.plot(dt,it,'x',c=colors[i],label=loc+' '+tt)

        i=i+1

#plot the transect leg 4 data
inpath_table = '../data/MCS/MP/'
fname = inpath_table+'ts_1m_gridded_melt.csv'

dt = getColumn(fname,0); dt = [ datetime.strptime(dt[x], "%Y%m%d") for x in range(len(dt)) ]
snod = getColumn(fname,1);snod = np.array(snod,dtype=np.float)
snod_std = getColumn(fname,2);snod_std = np.array(snod_std,dtype=np.float)
it = getColumn(fname,5);it = np.array(it,dtype=np.float)

ax.errorbar(dt,snod,snod_std,linestyle='None',c='y', marker='x',label='melt period')
bx.plot(dt,it,'x',c='y',label='melt period')

##plot the coring data
##for FYI deformed: maybe we can extrapolate to Sloop last measurement in the ridges - based on what we saw on initial survay in July!
#fnames = ['FYI_snow_clean.csv',
          #'SYI_snow_clean.csv']

#for fn in fnames:
    #fname = glob(inpath_coring+fn)[0]
    #print(fname)

    ##b'date,snow depth (m),snow depth std (m),ice thickness (m),ice thickness std (m),ice mode (m)\n'

    #dates = getColumn(fname,10)
    #dt = [ datetime.strptime(x, '%m/%d/%Y %H:%M') for x in dates ]
    #snod = getColumn(fname,1);snod = np.array(snod,dtype=np.float)/100
    #it = getColumn(fname,13);it = np.array(it,dtype=np.float)/100

    #age=fn.split('_')[0]

    #ax.plot(dt,snod,'.',label='coring '+age)
    #bx.plot(dt,it,'.',label='coring '+age)

#compare to accumulated snowfall from observations
inpath='../data/SnowModel/'
outpath='../plots_sm/'

fname = inpath+'final_10m_3hrly_met_forcing.dat'
print(fname)

results = csv.reader(open(fname))
#get rid of all multi-white spaces and split in those that remain
results_clean = [re.sub(" +", " ",row[0]) for row in results]

#precipitation
pp = [row.split(" ")[6] for row in results_clean]
pp = np.array(pp,dtype=np.float)     
pp = np.ma.array(pp,mask=pp==-9999)#/10  #match Glen's plot #WARNING - please chck if this is OK!

#different accumulation dates: 1 Sept, 1 Oct, 1 Nov
mask09=np.zeros_like(pp);mask09[31*8:]=1
mask10=np.zeros_like(pp);mask10[(31+15)*8:]=1
mask11=np.zeros_like(pp);mask11[(31+30+31)*8:]=1

#cumulative snowfall, convert to meters
pp_cum09 = np.cumsum(pp*mask09/1000)    
pp_cum10 = np.cumsum(pp*mask10/1000)
pp_cum11 = np.cumsum(pp*mask11/1000)

#dates
numdays=366*8
start = datetime(2019,8,1)
dt = [start + timedelta(hours=x*3) for x in range(numdays)]
end = datetime(2020,8,1)

#ax.plot(dt,pp_cum09,c='k',ls='--',label='snowfall Sep SWE')
#ax.plot(dt,pp_cum10,c='0.5',ls='--',label='snowfall Oct SWE')
#ax.plot(dt,pp_cum11,c='0.75',ls='--',label='snowfall Nov SWE')
    
ax.legend(ncol=5,fontsize=14,loc='upper left')
bx.legend(ncol=3,fontsize=14)

ax.tick_params(axis="x", labelsize=14)
ax.tick_params(axis="y", labelsize=14)

bx.tick_params(axis="x", labelsize=14)
bx.tick_params(axis="y", labelsize=14)

ax.set_ylim(0,.6)
bx.set_ylim(0,2.6)

#just winter = we have data
ax.set_xlim(datetime(2019,10,15),datetime(2020,7,29))
ax.set_xlim(datetime(2019,10,15),datetime(2020,7,29))

#nicer dates
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
ax.xaxis.set_minor_locator(MonthLocator())
ax.xaxis.set_major_formatter(DateFormatter('%b %Y'))
bx.xaxis.set_minor_locator(MonthLocator())
bx.xaxis.set_major_formatter(DateFormatter('%b %Y'))

plt.show()
#fig1.savefig(outpath+'ts_ice_type_forSnowModel.png',bbox_inches='tight')



#Paper/modeling work outline with a smarter assimilation/validation/budget procedure:
#1: Do not use any correction of atmospheric data based on the transect data (no snow depth assimilation). The reanalysis is already bias corrected to observations from precipitation radar and met tower.
#UPDATE: I treid to compare SWE in snow depth. The difference between KAZAR precip and snow depth is still unrealistically high. We could bias correct the precipitation by assimilating the best fit curve. The deviation from this curve measured by weekly transects can be then used for estimating D term. D is source in ridges and sink on level ice. We know from literature (Wagner et al) that all precip his high biased. This is mainly due to all the drifting snow and diamond dust. Maybe all we need to assimulate is one date at the end of the observations, 7 May! Use only Nloop because Sloop had a lead included into the last observations and is not representative.
#2: Assimilate snow density from snow pits (polynomic fit). Use snow sublimation due to snow transport (wind speed and humidity). Do this for three starting dates: (approximately: Nloop=thick SYI from August on, Sloop=thin SYI with melt ponds from 1 October on, runway=FYI from 1 November on)
#3: Run the SnowModel with these atmospheric forcing and snow density assimilated. We get 3 different mean snow depths time series over 3 ice types of different age (see previous point) in the CO. This should be (a bit) high-biased as we do not account for the snow removed into open leads and new ridges. In case it is low biased, we need to rethink the whole concept in the following points!
#3a: In case this is very high biased and does not fit with our findings in the following steps (it does not fall somewhere between observed level and deformed ice snow depth), we can introduce a sink term for deformation here. This sink term represents the amount of snow removed into leads with open water and into fresh ridges. We can compare this sink to the total sea ice deformation time series that we already made from buoys (I think comparison should be enough - we dont need to use the deformation data directly, a simple linear correlation plot of smoothed deformation data would be great). A reasonable value for this could be ~10%. Because we can not imagine any other sink we take it into account and update the snow SWE/mass balance equation (from Liston et al, 2020, low resolution SnowModel-LG) that already includes a similar sink. This can be the improved 'D' term. In case such updated sink term is not needed, we also describe this as a finding in our paper. If we decide to use this sink, we need to re-run the model with the 'D term' removing some snow at each time step - in fact exactly like snow depth from observations was assimilated, except here we only take away, we dont add snow.
#4: Take the snow depth time series and 3 different ice ages and distribute it into two classes: level and deformed. We get this by scaling the snow depth to fit best the linear model fitted to seasonal observations (See attached figure). The scaling factors will change seasonally. The deformed ice scaling factor becomes higher and higher and level ice scaling factor becomes lower and lower through the season. We do this for all 3 transects of different age (Sloop, Nloop, runway). Using the modelled fit to the observations is a good idea as the weekly transect measurements include some random increases and decreases. Those are caused by small sample numbers and sensitivity to changes in predominant wind direction changes (affecting both level ice snow dunes and snow drifts behind ridges). Now we have perfectly scaled snow cover fitting approximately to observation from transects over different ice ages and types. The scaling between level and deformed ice snow depth stays same after beginning of May (no more snow observations over those locations and melt snow observations are questionable - snow combined with rotten ice surface). All this is done offline - after the SnowModel runs under point 3 (or 3a).
#4a: As a check if our work is reasonable, we can take snow depth from point 4 and calculate fraction of level ice (x) needed (deformed ice is 1-x) to get mean snow depth from point 3. One would expect a steady decrease from ~90% to ~50% over the season. We can also use a satellite image to estimate approximately the fractions of each ice age inside a box of 2 km by 2 km - this is some kind of 'back of the envelope calculation'.
#5: We use the snow cover from point 4 as forcing to HIGTSI. We take known ocean heat flux. We estimate snow thermal conductivity so that it develops seasonally like snow density (from snow pits and from SnowModel) and we get reasonable sea ice thickness compared to the observations (also see attached figure). This can stay a 'fudge factor' until SeaiCE-3D is developed. Some discussion in the paper would be nice, but we may not want to get to the bottom of this problem here. I really need your opinion in this.
#6: We compare sea ice thickness from our runs (in total 6 runs, 2 runs - level and deformed for each transect) to sea ice thickness observed in transect. The sea ice thickness in the ridges will not change and the snow depth there wont be important for the ice growth. Still, it will be nice time series of snow accumulation there. Also, if we can use the right ocean heat fluxes, the ice there will start to melt in April. We will also show how the snow on deformed stays longer in summer before it melts.
#7: We plot all the time series of all snow mass balance equation terms. Especially snow sublimation and deformation sink will be informative and useful for discussion.
#8: For later work (collaboration with the heat flux group) and as checks for us we should also: plot all the atmosphere, snow, ice, ocean heat fluxes (model variables need to be saved). These are heat fluxes separate for each ice type and not aggregated for the whole CO (fractions are not really known). To get those we would need to run the model in 3D (maps of snow distribution) - but that we wont do here, that will be our next step...

#Some things to think about:
#-Are we still missing anything critical right now: yes: ocean surface heat fluxes. But we can start for now with 2W/m2.

#-Is the bulk snow density same on level ice and in the much deeper snow pack in the ridges? What can we do about it if we think it is not the same? Does this matter a lot?

#-Do we still need any model development? Yes, but only small things: 1) snow sink due to deformation; 2) tuning of the snow thermal conductivity

#-How can we do this efficiently? I got explanations and from you (I hope I remember most of it, we also made good notes right into the text files). Can I get access to your machine and try? Or should I try to install and install SnowModel+HIGTSI here locally. I have an Ubutnu server I can use at UiT. And you have experience helping people with gfortran.
