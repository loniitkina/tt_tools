import numpy as np
from glob import glob
from tt_func import getColumn
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

ts=True
pdf=False
rates=True

##grid spacing
#stp = '5m'
#stp = '2m_linear'
#stp = '2m_nearest'

inpath_grid = '../data/grids/'
inpath_grid = '../data/grids_AGU/'
inpath_table = '../data/MCS/MP/'
outpath = '../plots_AGU/'


##two dates
#dates = ['20191219','20200220']
#dates = ['20191226','20200220']
#dates = ['20200102','20200220'] #platelet ice paper
#dates = ['20200112','20200207'] #gnss paper
#dates = ['20191107','20200426'] #start and end of winter, S loop
#dates = ['20191205','20200305'] #start and end of winter, N loop

#datel = ['2020/01/02','2020/02/20'] 
#datel = ['2020/01/12','2020/02/07']

#colors = ['blue','green']

#outname = 'pdf_'+loc+'_early26.png'
#outname = 'pdf_'+loc+'_platelet.png'
#outname = 'pdf_'+loc+'_gnss.png'

#select location
loc = 'Nloop'
title='Northern transect loop'
dates =['20191024','20191031','20191107','20191114','20191121','20191128','20191205',  '20191219','20191226','20200102','20200109','20200116','20200130','20200206','20200220','20200227', '20200305','20200320','20200326','20200403','20200416','20200424','20200430','20200507'] 


#loc = 'Sloop'
#title='Southern transect loop'
#dates = ['20191031','20191107','20191114','20191205',   '20191226','20200102','20200109','20200116','20200130','20200206','20200220','20200227','20200305','20200330','20200406','20200426','20200507']


#loc = 'snow1'
#title='Snow1 Transect'
#dates = ['20191222','20200112','20200126','20200207','20200223','20200406']

#loc = 'runway'
#title='Runway Transect'
#dates = ['20200112','20200119','20200207']

##leg4
#loc = 'transect'
#title = 'Leg 4 Transect '
###all data
#dates = ['20200627','20200628','20200629','20200630','20200702','20200703','20200704','20200705','20200706','20200707','20200708','20200710','20200713','20200714','20200716','20200719','20200720','20200721','20200723','20200725','20200726','20200727']

#loc = 'albedoLD'
#title = 'Lemon Drop albedo line '
#dates = ['20200630','20200706','20200707','20200719','20200721','20200724','20200727']

#loc = 'albedoRBB'
#title = 'Root Beer Barrel albedo line '
#dates = ['20200714','20200717','20200630','20200706','20200707','20200719','20200727']

##leg5
#loc = 'albedoK'
#title = 'Kinder albedo line '
#dates = ['20200824','20200830','20200903','20200907','20200910','20200918']

#loc = 'ARIEL'
#title = 'Ariel transect'
#dates = ['20200830','20200903','20200907','20200910','20200917']

#loc = 'kuka'
#title = 'KuKa transect'
#dates = ['20200907','20200910','20200917']



loc='special'
title = 'Special Transects '
#dates = ['20200107','20200115','20200123','20200226','20200326','20200403','20200430','20200617','20200719','20200719','20200709','20200827','20200903','20200910','20200902','20200909','20200919']
dates = ['20200107','20200115','20200123','20200226','20200326','20200430','20200617','20200719','20200719','20200827','20200903','20200910','20200902','20200909','20200919']


combo=False



##combinations
#combo=True
#loco = 'combi'
#loc = 'Sloop'
#title = 'Combined MOSAiC Transects '
#dates = ['20191031','20191107','20191114','20191205',   '20191226','20200102','20200109','20200116','20200130','20200206','20200220','20200227','20200305','20200330','20200406','20200426','20200507',
#'20200617','20200630','20200706','20200714','20200719','20200726',
#'20200827','20200903','20200910']   #port transects of leg 5
##'20200830','20200903','20200907','20200910','20200918']    #short transects in CO of leg 5 (thick ice!)

#colors = plt.cm.rainbow(np.linspace(0, 1, len(dates)))
#datel=dates
outname = 'pdf_'+loc+'_all.png'
outname = 'pdf_'+loc+'_ice.png'
#outname_ts = 'ts_'+loc+'_'+stp+'.png'
#outname_ts_type = 'ts_'+loc+'_'+stp+'_type.png'

outname_ts = 'ts_'+loc+'_'+'1m_gridded_it1.png'
file_ts = inpath_table+'ts_'+loc+'_'+'1m_gridded.csv'
outname_ts_type = 'ts_'+loc+'_'+'1m_gridded_it_type.png'

##events (selected dates from leg 1-3)
#dates = ['20191107','20191205','20200227','20200426'] #Sloop
#dates = ['20191107','20191205','20200227','20200430'] #Nloop

colors = plt.cm.rainbow(np.linspace(0, 1, len(dates)))
if combo==True:
    #add some grey shading into the box plots for the dates when transects were not in the winter locations (Sloop)
    #make rainbow colors for the Sloop
    colors = plt.cm.rainbow(np.linspace(0, 1, len(dates)-9))
    #print(colors)
    #add grey color for leg 4 dates
    colors = np.append(colors,[[.5,.5,.5,.5]],axis=0)
    colors = np.append(colors,[[.5,.5,.5,.5]],axis=0)
    colors = np.append(colors,[[.5,.5,.5,.5]],axis=0)
    colors = np.append(colors,[[.5,.5,.5,.5]],axis=0)
    colors = np.append(colors,[[.5,.5,.5,.5]],axis=0)
    colors = np.append(colors,[[.5,.5,.5,.5]],axis=0)

    #and grey colors for leg 5 dates
    colors = np.append(colors,[[.5,.5,.5,.5]],axis=0)
    colors = np.append(colors,[[.5,.5,.5,.5]],axis=0)
    colors = np.append(colors,[[.5,.5,.5,.5]],axis=0)    
    #print(colors)
    
    
#datel=dates
#outname = 'pdf_'+loc+'_events.png'



hem=True        #use HEM means and modes provided by Luisa
inpath_hem = '../data/HEM_Luisa/'
fname = inpath_hem+'Ice_thickness_properties.txt'
dt_hem= getColumn(fname,1, delimiter='\t')
loc_hem= getColumn(fname,2, delimiter='\t')
m_hem= getColumn(fname,3, delimiter='\t')
mo_hem= getColumn(fname,4, delimiter='\t')
dt_hem = [ datetime.strptime(x, '%Y-%m-%d') for x in dt_hem ]
m_hem = np.array(m_hem,dtype=np.float)
mo_hem = np.array(mo_hem,dtype=np.float)

#print(dt_hem)
#exit()

cs2=True    #use CS2 total ice thickness provided by Stefan (for Krumpen et al, 2021)
inpath_cs2 = '../data/CS2/'
fname = inpath_cs2+'l2p-extract-sit-0050km-20191001-20200430.csv'
dt_cs2= getColumn(fname,0)
m_cs2= getColumn(fname,4)
dt_cs2 = [ datetime.strptime(x, '%Y-%m-%d') for x in dt_cs2 ]
m_cs2 = np.where(m_cs2=='','0',m_cs2)
m_cs2[m_cs2=='']='0'    #replace empty strings with values
m_cs2 = np.array(m_cs2,dtype=np.float)
m_cs2 = np.ma.array(m_cs2,mask=m_cs2==0)

fname = inpath_cs2+'l2p-extract-sd-0050km-20191001-20200430.csv'
m_cs2sd= getColumn(fname,4)
m_cs2sd = np.where(m_cs2sd=='','0',m_cs2sd)
m_cs2sd[m_cs2sd=='']='0'    #replace empty strings with values
m_cs2sd = np.array(m_cs2sd,dtype=np.float)
m_cs2sd = np.ma.array(m_cs2sd,mask=m_cs2sd==0)

#m_cs2 = m_cs2-m_cs2sd

irbins = np.arange(0,5,.05)
if pdf==True:
    #PDFs
    fig1 = plt.figure(figsize=(10,10))
    #fig1.suptitle(title, fontsize=30)
    #ax = fig1.add_subplot(111)
    ##ax.set_title('S transect loop')
    #ymax=.2
    #ax.set_ylim(0,ymax)
    #ax.set_xlabel('Snow depth (m)', fontsize=20)
    #ax.set_ylabel('Probability', fontsize=20)
    #srbins = np.arange(0,.8,.02)
    #ax.tick_params(axis="x", labelsize=14)
    #ax.tick_params(axis="y", labelsize=14)
    #ax.set_xlim(0,.5)

    bx = fig1.add_subplot(111)
    #bx.set_title('S transect loop')
    ymax=.5
    bx.set_ylim(0,ymax)
    bx.set_xlabel('Ice thickness (m)', fontsize=20)
    bx.set_ylabel('Probability', fontsize=20)
    bx.tick_params(axis="x", labelsize=14)
    bx.tick_params(axis="y", labelsize=14)
    bx.set_xlim(0,2)

#store data for time series
ts_snow=[]
ts_ice=[]
ts_mo=[]
ts_snow_m=[]
ts_snow_std=[]
ts_ice_m=[]
ts_ice_std=[]
#level and deformed ice
ts_snow_l=[]
ts_snow_d=[]

i=0
for date in dates:
    print(date)
    
    if combo == True:
        datei = datetime.strptime(date, '%Y%m%d')

        if datei < datetime(2020,6,1):
            loc='Sloop'
        elif datei > datetime(2020,8,15):
            #loc='albedoK'
            loc='special'
        else:
            loc='transect'
            
        print(loc)

    ##load all the gridded data created in tt_grid.py
    #if loc == 'both':
        
        #of = inpath_grid+'Nloop'+'_'+date+'_'+stp+'.npz'
        #data = np.load(of)
        #snod1 = data['snow']
        #it1 = data['ice']
        
        #of = inpath_grid+'Sloop'+'_'+date+'_'+stp+'.npz'
        #data = np.load(of)
        #snod2 = data['snow']
        #it2 = data['ice']  
        
        #snod = np.nan_to_num(snod1, nan=0)+np.nan_to_num(snod2, nan=0)
        #it = np.nan_to_num(it1, nan=0)+np.nan_to_num(it2, nan=0)
        #snod = np.ma.array(snod,mask=snod==0)
        #it = np.ma.array(it,mask=it==0)
        
    #else:   
        #of = inpath_grid+loc+'_'+date+'_'+stp+'.npz'
        #print(of)
        #data = np.load(of)
        #snod = data['snow']
        #it = data['ice']
     
        ##get rid of nans
        #m1 = np.ma.masked_invalid(it)
        ##it = np.ma.masked_invalid(it)
        
    #snod = snod[m1.mask == False]
    #it = it[m1.mask == False]
    
    #load the csv data created in tt_grid.py
    fname = glob(inpath_table+'*/magna+gem2-transect-'+date+'*'+loc+'*.csv')[0]
    snod = getColumn(fname,5)
    it = getColumn(fname,8)
    if date=='20200206' or date=='20200406':
        it = getColumn(fname,9)     #bad instrument performance on that date, 63kHz q is best
        
    snod = np.array(snod,dtype=np.float)
    it = np.array(it,dtype=np.float)
    
    #dummy data and negative value treatment (important for summer data)
    it = np.where(it==-1,0,it)
    snod = np.where(snod==-1,0,snod)
    
    #in summer there can be negative thicknesses in salty melt ponds, set those to zero
    it = np.where(it<0,0,it)
    #and they have some bias (bad calibration?)
    if date=='20200903':
        it = np.where(it>0,it-.4,it)

    
    ##add some more measurements for leg5
    #if loc=='albedoK':
        #loc2='ARIEL'
        #date2=date
        #if date=='20200918':
            #date2='20200917'
        #fname = glob(inpath_table+'*/magna+gem2-transect-'+date2+'*'+loc2+'*.csv')[0]
        #tmps = getColumn(fname,5)
        #tmpi = getColumn(fname,6)
        #snod2 = np.array(tmps,dtype=np.float)
        #it2 = np.array(tmpi,dtype=np.float)
        
        #snod = np.append(snod,snod2)
        #it = np.append(it,it2)  
        ##print(it)
        ##exit()
    
    #means and modes
    mn = np.mean(np.ma.masked_invalid(snod).compressed())#.compressed()
    print(mn)
    print(np.std(snod))
    #mni = np.mean(it)
        
    #find mode
    it_pos = np.ma.array(it,mask=it==0);it_pos=it_pos.compressed()  #take only non-zero (not detected as negative) values
    hist = np.histogram(it_pos,bins=irbins)
    srt = np.argsort(hist[0])                           #indexes that would sort the array
    mm = srt[-1]                                        #same as: np.argmax(hist[0])
    mm1 = np.argmax(hist[0])
    mo = (hist[1][mm] + hist[1][mm+1])/2           #take mean of the bin for the mode value
    print(mo)
    
    if pdf==True:
        ##plot PDFs
        #weights = np.ones_like(snod) / (len(snod))
        #n, bins, patches = ax.hist(snod, srbins, histtype='step', color=colors[i], linewidth=4, alpha=.5, weights=weights, label=datel[i])
        #ax.plot([mn,mn],[0,ymax],c=colors[i],ls='--', label='mean = '+str(round(mn,2))+' m')

        weights = np.ones_like(it) / (len(it))
        n, bins, patches = bx.hist(it, irbins, histtype='step', color=colors[i], linewidth=4, alpha=.5, weights=weights, label=datel[i])
        bx.plot([mo,mo],[0,ymax],c=colors[i],ls='--', label='mode = '+str(round(mo,2))+' m')
        #bx.plot([mni,mni],[0,ymax],c='k',ls=':', label='mean = '+str(round(mni,2)))
    
    if ts==True:
        #save data for time series and export text files
        ts_snow.append(snod)
        ts_snow_m.append(mn)
        ts_snow_std.append(np.std(snod))
        #if date=='20200206' and loc == 'Sloop': continue #bad data for GEM-2 
        ts_ice.append(it)
        ts_mo.append(mo)
        ts_ice_m.append(np.mean(it))
        ts_ice_std.append(np.std(it))
        
        #separate deformed and level ice based on the mode
        #use this to separate the snow depth
        level_ice = (it>mo-.1) & (it<mo+.1)
        deformed_ice = (it>mo+.25)
        
        #level_ice = (it<2)
        #deformed_ice = (it>2.8)
        
        level_snow = np.ma.array(snod,mask=~level_ice)
        def_snow = np.ma.array(snod,mask=~deformed_ice)
        
        
        #scatter plots
        fig3 = plt.figure(figsize=(20,9))
        fig3.suptitle(date, fontsize=30)
        zx = fig3.add_subplot(121)
        zx.set_title('Level ice', fontsize=25)
        zx.set_xlabel('Ice thickness (m)', fontsize=20)
        zx.set_ylabel('Snow depth (m)', fontsize=20)
        zx.tick_params(axis="x", labelsize=16)
        zx.tick_params(axis="y", labelsize=16)

        zzx = fig3.add_subplot(122)
        zzx.set_title('Deformed ice', fontsize=25)
        zzx.set_xlabel('Ice thickness (m)', fontsize=20)
        zzx.set_ylabel('Snow depth (m)', fontsize=20)
        zzx.tick_params(axis="x", labelsize=16)
        zzx.tick_params(axis="y", labelsize=16)

        zx.scatter(it,level_snow,c=colors[0], alpha=0.5, s=30)
        zzx.scatter(it,def_snow,c=colors[0], alpha=0.5, s=30)
        
        outname_sc = 'scatter_'+loc+'_'+date+'.png'
        fig3.savefig(outpath+outname_sc,bbox_inches='tight')
        plt.close(fig3)

        #for time series    
        level_snow = np.ma.compressed(level_snow)
        def_snow = np.ma.compressed(def_snow)

        ts_snow_l.append(level_snow)
        ts_snow_d.append(def_snow)

        i = i+1
    

if pdf==True:
    print(outname)
    #ax.legend(fontsize=20)
    bx.legend(fontsize=20)

    fig1.savefig(outpath+outname,bbox_inches='tight')


if ts==True:
    if combo==False:    #dont do this for combo as it will just double the information
        #time series text file exports
        tt = [dates,ts_snow_m,ts_snow_std,ts_ice_m,ts_ice_std,ts_mo]
        table = list(zip(*tt))

        print(file_ts)
        with open(file_ts, 'wb') as f:
            #header
            f.write(b'Date/Time, snow depth mean, snow depth SD, ice thickness mean, ice thickness SD, ice thickness mode\n')
            np.savetxt(f, table, fmt="%s", delimiter=",")

    
    
    
    
    #time series plots
    fig2 = plt.figure(figsize=(20,10))
    cx = fig2.add_subplot(211)
    cx.set_title(title, fontsize=25)
    cx.set_ylabel('Snow depth (m)', fontsize=20)
    cx.tick_params(axis="x", labelsize=14)
    cx.tick_params(axis="y", labelsize=14)
    cx.set_ylim(0,.9)

    dx = fig2.add_subplot(212)
    dx.set_ylabel('Ice thickness (m)', fontsize=20)
    dx.tick_params(axis="x", labelsize=14)
    dx.tick_params(axis="y", labelsize=14)
    
    if loc=='Sloop': 
        dx.set_ylim(0,4)
    elif loc=='Nloop':
        dx.set_ylim(0,11)
    elif loc=='transect': 
        dx.set_ylim(0,5)
    elif loc=='snow1': 
        dx.set_ylim(0,4)
    else:
        dx.set_ylim(0,5)

    #spacing between the box plots
    dt = [ datetime.strptime(x, '%Y%m%d') for x in dates ]
    
    #get leg 5 as start of MOSAiC
    
    if combo==True:
        
        dt1 = [ x-timedelta(days=366) for x in dt if x > datetime(2020,8,1)  ]
        
        dt[-3:] = dt1   #check how many transect we have (3 for special, 5 for albedoK)
        
    #import ipdb;ipdb.set_trace()
    
    dt_diff = [ (x-dt[0]).days for x in dt ]

    #this is a very ugly trick: positions needs at least len=2...
    for i in range(0,len(dates)):
        cx.boxplot([ts_snow[i],ts_snow[i]], notch=True, showfliers=False, positions=[dt_diff[i],dt_diff[i]],widths=5,patch_artist=True,
                boxprops=dict(facecolor=colors[i],alpha=.4))

    for i in range(0,len(dates)):
        dx.boxplot([ts_ice[i],ts_ice[i]], notch=True, showfliers=False, positions=[dt_diff[i],dt_diff[i]],widths=5,patch_artist=True,
                boxprops=dict(facecolor=colors[i],alpha=.4))
        
    dx.plot(dt_diff,ts_mo,'s',ms=15, label='mode',c='0.3')

    

    #and a dirty trick for the X axis    
    if combo==True:
        dates_m = ['20190901','20191001','20191101','20191201','20200101','20200201','20200301','20200401','20200501','20200601','20200701','20200801']
        dt_m = [ datetime.strptime(x, '%Y%m%d') for x in dates_m ]
        dt_diff_m = [ (x-dt[0]).days for x in dt_m ]
        plt.xticks(dt_diff_m, ['1 Sep','1 Oct','1 Nov','1 Dec','1 Jan','1 Feb','1 Mar','1 Apr','1 May','1 Jun','1 Jul','1 Aug'])
    else:
        dates_m = ['20191101','20191201','20200101','20200201','20200301','20200401','20200501']
        dt_m = [ datetime.strptime(x, '%Y%m%d') for x in dates_m ]
        dt_diff_m = [ (x-dt[0]).days for x in dt_m ]
        plt.xticks(dt_diff_m, ['1 Nov','1 Dec','1 Jan','1 Feb','1 Mar','1 Apr','1 May'])

    
    if hem:
        
        dt1 = [ x-timedelta(days=366) for x in dt if x > datetime(2020,8,1)  ]
        
        print(dt1)
        
        
        dt_hem[-1:] = dt1
        
        print(dt_hem)
        
        
        dt_diff_hem = [ (x-dt[0]).days for x in dt_hem ]
        
        print(dt_diff_hem)
        #exit()
        
        for hl in range(0,len(loc_hem)):
            if loc_hem[hl]=='(DN)':
                if hl==1:
                    dx.plot(dt_diff_hem[hl],mo_hem[hl],'s',ms=10, markeredgecolor='k', label='HEM mode',c='r')
                    dx.plot(dt_diff_hem[hl],m_hem[hl],'d',ms=10, markeredgecolor='k',label='HEM mean',c='r')
                else:
                    dx.plot(dt_diff_hem[hl],mo_hem[hl],'s',ms=10, markeredgecolor='k',c='r')
                    dx.plot(dt_diff_hem[hl],m_hem[hl],'d',ms=10, markeredgecolor='k',c='r')
    
    if cs2:
        
        dt_diff_cs2 = [ (x-dt[0]).days for x in dt_cs2 ]
        
        cx.plot(dt_diff_cs2,m_cs2sd,'.',label='CS-2 snow',c='.75')
        
        dx.plot(dt_diff_cs2,m_cs2,'.',label='CS-2 mean',c='.75')
        
        
        #for hl in range(0,len(loc_hem)):
            #if loc_hem[hl]=='(DN)':
                #if hl==1:
                    
                    #dx.plot(dt_diff_hem[hl],m_hem[hl],'.',ms=10, markeredgecolor='k',label='HEM mean',c='r')
                #else:
                    
                    #dx.plot(dt_diff_hem[hl],m_hem[hl],'d',ms=10, markeredgecolor='k',c='r')
    
    
    dx.legend(fontsize=20)
    
    cx.set_xticks(dt_diff_m)
    fig2.autofmt_xdate()

    fig2.savefig(outpath+outname_ts,bbox_inches='tight')
    plt.close(fig2)

    ###time series of deformed/level snow and ice 
    #fig4 = plt.figure(figsize=(20,5))
    #cx = fig4.add_subplot(111)
    #cx.set_title(title, fontsize=25)
    #cx.set_ylabel('Snow depth (m)', fontsize=20)
    #cx.tick_params(axis="x", labelsize=14)
    #cx.tick_params(axis="y", labelsize=14)
    #cx.set_ylim(0,1)

    ##spacing between the box plots
    #dt = [ datetime.strptime(x, '%Y%m%d') for x in dates ]
    #dt_diff = [ (x-dt[0]).days for x in dt ]
    #dt_diff_off = [ (x-dt[0]).days+3 for x in dt ]

    ##snow on level ice
    #bp1=cx.boxplot(ts_snow_l, notch=True, showfliers=False, positions=dt_diff,widths=3,patch_artist=True,
                #boxprops=dict(facecolor=colors[2],alpha=.4))

    ##snow in ridges
    #bp2=cx.boxplot(ts_snow_d, notch=True, showfliers=False, positions=dt_diff_off,widths=3,patch_artist=True,
                #boxprops=dict(facecolor=colors[4],alpha=.4))

    ##and a dirty trick for the X axis
    #dates_m = ['20191101','20191201','20200101','20200201','20200301','20200401','20200501']
    #dt_m = [ datetime.strptime(x, '%Y%m%d') for x in dates_m ]
    #dt_diff = [ (x-dt[0]).days for x in dt_m ]
    #plt.xticks(dt_diff, ['1 Nov','1 Dec','1 Jan','1 Feb','1 Mar','1 Apr','1 May'])
    #cx.set_xticks(dt_diff)
    #fig4.autofmt_xdate()

    #cx.legend([bp1["boxes"][0], bp2["boxes"][0]], ['level ice', 'deformed ice'], loc='upper left', fontsize=20)

    #fig4.savefig(outpath+outname_ts_type,bbox_inches='tight')


