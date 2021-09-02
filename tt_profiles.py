import numpy as np
from glob import glob
from tt_func import getColumn
from scipy.signal import savgol_filter
from datetime import datetime
import matplotlib.pyplot as plt

##grid parameters
#stp = '5m'
#stp = '2m_linear'
#stp = '2m_nearest'
#maxdist = 10   #how far away to search in case of nan
##maxdist = 5

#window size for savgol smoothing savgol_filter (must be odd and more than polyorder=3)
polyorder=3
widow=21
window=5
##for point measurements (like ridges)
#polyorder=0
#window=1

#location and dates
loc = 'Sloop'

dates = ['20191031','20191107','20191114','20191205',   '20200102','20200109','20200116','20200130','20200206','20200220','20200227','20200305','20200330','20200426','20200507']

#dates = ['20191031','20191107','20191114','20191205',   '20191226','20200102','20200109','20200116','20200130','20200206','20200220','20200227','20200305','20200330','20200426','20200507']    #best data

dates = ['20191031','20191107','20191114','20191205',   '20191226','20200102','20200109','20200116','20200130','20200206','20200220','20200227','20200305','20200330','20200406','20200426','20200507']

title='Southern transect loop '

loc = 'Nloop'
dates = ['20191205','20191219','20200220','20200227','20200305','20200416','20200507']

dates = ['20191024','20191031','20191107','20191114','20191121','20191128','20191205',  '20191219','20191226','20200102','20200109','20200116','20200130','20200206','20200220','20200227', '20200305','20200320','20200326','20200403','20200416','20200424','20200430','20200507']




title='Northern transect loop '

#loc = 'Nloop_spine'
#dates = ['20191205','20191219','20200220','20200227','20200305','20200424','20200507']
#datel = ['2019/12/05','2019/12/19','2020/02/20','2020/02/27','2020/03/05','2020/04/24','2020/05/07']
#title='Northern transect loop spine '




loc= 'snow1'
dates = ['20191222','20200112','20200126','20200207']    #20200126 is reduced track (square!)
dates = ['20200126']
title='Snow1 transect '

#loc= 'special'
#dates = ['20200123']
#datel = ['2020/01/23']
#title='Long transect '

#loc = 'ridgeFR1'
#dates = ['20200108']#,'20200119','20200221']#,'20200305']
#datel = ['2020/01/08']#,'2020/01/19','2020/02/21']#,'2020/03/05']
#title = 'Fort Ridge Installation Transect '

#loc = 'ridgeFR2'    #coring
#dates = ['20200110']#,'20200212','20200221']
#datel = ['2020/01/10']#,'2020/02/12','2020/02/21']
#title = 'Fort Ridge Coring Transect '

#loc = 'ridgeFR3'
#dates = ['20200131']
#datel = ['2020/01/31'] 
#title = 'Fort Ridge Optics Transect '

#loc = 'ridgeA1'    #central
#dates = ['20200117']#,'20200131','20200228']#,'20200410']
#datel = ['2020/01/17']#,'2020/01/31','2020/02/28']#,'2020/04/10']
#title = "Allie's Ridge Central Transect "




#loc = 'ridgeA2'    #north
#dates = ['20200212','20200228','20200410']
#datel = ['2020/02/12','2020/02/28','2020/04/10']
#title = "Allie's Ridge North Transect "

#loc = 'ridgeA3'    #south
#dates = ['20200212','20200228','20200410']
#datel = ['2020/02/12','2020/02/28','2020/04/10']
#title = "Allie's Ridge South Transect "

#loc = 'ridgeD'  #David's Ridge
#dates = ['20200410','20200416','20200424','20200430','20200507']
#datel = ['2020/04/10','2020/04/16','2020/04/24','2020/04/30','2020/05/07']
#title = "David's Ridge Transect "

#loc = 'ridgeE'  #ECO Ridge (lead?)
#dates = ['20200424']
#datel = ['2020/04/24']
#title = "ECO Ridge Transect "

##comparable loop transects
#loc = 'Sloop'
#dates = ['20200130']
#datel = ['2020/01/30']
#title='Southeren transect loop '

#loc = 'runway'
#dates = ['20200207']
#datel = ['2020/02/07']
#title='Runway transect '

#dates = ['20200107']
#datel = ['2020/01/07']
#title='Dark Side FYI '

#dates = ['20200115']
#datel = ['2020/01/15']
#title='Dark Side SYI '


##Nansen Legacy
#loc='P4'
#dates = ['20210505']
#title='Nansen Legacy Q2 - P4 '

#loc='P5'
#dates = ['20210508']
#title='Nansen Legacy Q2 - P5 '

##loc='P6'
##dates = ['20210510']
##title='Nansen Legacy Q2 - P6 '

#loc='P7'
#dates = ['20210513']
#title='Nansen Legacy Q2 - P7 '



dt = [ datetime.strptime(x, '%Y%m%d') for x in dates ]
datel = [ datetime.strftime(x, '%Y/%m/%d') for x in dt ]


print(loc)
#colors = plt.cm.rainbow(np.linspace(0, 1, len(dates)))
colors = plt.cm.Blues(np.linspace(0, 1, len(dates)))

if len(dates) == 1:
    colors = ['.1','.5']
    
#MOSAiC
inpath_table = '../data/MCS/MP/'
outpath = '../plots_AGU/'
inpath_grid = '../data/grids_AGU/'

##Nansen Legacy
#inpath_table = '../data/NansenLegacy/magnaprobe/'
#outpath = '../plots_NL/'

station = True
#station = False

fb_list=[]
si_list=[]
ii_list=[]
x_list=[]

for dd in range(0,len(dates)):
    date = dates[dd]
    print(date)

    if station:
        outname = 'profile_'+date+'_'+loc+'gridded.png'
        
        #choose one 'most perfct' MP track to compare to the others
        fname = glob(inpath_table+'*/magna+gem2*'+date+'*'+loc+'.csv')[0]
        print(fname)
        mxx = getColumn(fname,3, delimiter=',', magnaprobe=False)
        myy = getColumn(fname,4, delimiter=',', magnaprobe=False)
        snod = getColumn(fname,5, delimiter=',', magnaprobe=False)
        
        if 'ridge' in loc:
            #Date,Lon,Lat,X,Y,Snow,f1525Hz_hcp_i,f1525Hz_hcp_q,f5325Hz_hcp_i,f5325Hz_hcp_q,18325Hz_hcp_i,f18325Hz_hcp_q,f63025Hz_hcp_i,f63025Hz_hcp_q,f93075Hz_hcp_i,f93075Hz_hcp_q
            it = getColumn(fname,6, delimiter=',', magnaprobe=False)
            it2 = getColumn(fname,7, delimiter=',', magnaprobe=False)
            it3 = getColumn(fname,8, delimiter=',', magnaprobe=False)
            it4 = getColumn(fname,9, delimiter=',', magnaprobe=False)
            it5 = getColumn(fname,10, delimiter=',', magnaprobe=False)       #closer to real thickness, but still influenced by consolidation (has detection limit)
            it6 = getColumn(fname,11, delimiter=',', magnaprobe=False)       #consolidation can be seen in column 13 (63kHz q) and 15 (93kHz q)
            it7 = getColumn(fname,12, delimiter=',', magnaprobe=False)
            it8 = getColumn(fname,13, delimiter=',', magnaprobe=False)
            it9 = getColumn(fname,14, delimiter=',', magnaprobe=False)
            it10 = getColumn(fname,15, delimiter=',', magnaprobe=False)
            
            it2 = np.array(it2,dtype=np.float)
            it3 = np.array(it3,dtype=np.float)
            it4 = np.array(it4,dtype=np.float)
            it5 = np.array(it5,dtype=np.float)
            it6 = np.array(it6,dtype=np.float)
            it7 = np.array(it7,dtype=np.float)
            it8 = np.array(it8,dtype=np.float)
            it9 = np.array(it9,dtype=np.float)
            it10 = np.array(it10,dtype=np.float)
            
        else:
            it = getColumn(fname,6, delimiter=',', magnaprobe=False)
        mxx = np.array(mxx,dtype=np.float)
        myy = np.array(myy,dtype=np.float)
        si = np.array(snod,dtype=np.float)
        ii = np.array(it,dtype=np.float)
        
        #it looks like they started somewhere else the last two times, still went same direction...
        if date=='20200330' or date=='20200426':
            #fb = np.concatenate((fb[-215:],fb[:-215]))
            ii = np.concatenate((ii[-215:],ii[:-215]))
            si = np.concatenate((si[-215:],si[:-215]))
    else:
        #not a single data collection station, but a camp with several repeats over same transect
    
        #alternativelly, completely gridded data (snow too!)
        #step = 2
        step = 1
        stp = str(step)
        method_gem2 = 'nearest'
        #method_gem2 = 'linear'
        ch_name = '_18kHz'

        outname = loc+'_profile_'+date+'_'+stp+'_gridded_full.png'
        #inf = inpath_grid+loc+'_'+stp+'m_'+method_gem2+ch_name+'_track_test.npz'
        inf = inpath_grid+loc+'_'+stp+'m_'+method_gem2+ch_name+'_track.npz'
        
        data = np.load(inf)

        transect_snow = data['snow']
        transect_ice = data['ice']
        
        del data
        
        mxx = transect_snow[:,0]
        myy = transect_snow[:,1]
        si = transect_snow[:,dd+2]
        it = transect_ice[:,dd+2]
        
        it = np.ma.masked_invalid(it)
        si = np.ma.array(si,mask=it.mask)
        mxx = np.ma.array(mxx,mask=it.mask); mxx = mxx.compressed()
        myy = np.ma.array(myy,mask=it.mask); myy = myy.compressed()
        
        si = si.compressed()
        ii = it.compressed()
    
    #get distances between fixed date MP points
    dx = mxx[1:]-mxx[:-1]
    dy = myy[1:]-myy[:-1]
    md = np.sqrt(dx**2+dy**2)

    #what is the surface elevation? ALS geotiff???
    #hydrostatic equilibrium with mean snow density and sea ice density
    rho_i = 882
    rho_w = 1025
    rho_s = 313

    #plot
    fig1 = plt.figure(figsize=(20,10))
    #fig1 = plt.figure(figsize=(40,20))
    fig1.patch.set_facecolor('0.5')
    fig1.patch.set_facecolor('1')
    
    ax = fig1.add_subplot(111)
    ax.set_xlabel('Length (m)', fontsize=25)
    ax.set_title(title+datel[dd], fontsize=30)
    ax.set_ylabel('Distance from water surface (m)', fontsize=25)
    ax.tick_params(axis="x", labelsize=24)
    ax.tick_params(axis="y", labelsize=24)
    if station:
        ax.set_facecolor('0.8')
    else:
        ax.set_facecolor('0.3')
    
    #if loc=='Sloop' and date == '20191226':
        #bad = np.zeros_like(ii)
        #bad[700:] = 1
        #ii = np.ma.array(ii,mask=bad)

    #what is the surface elevation? ALS geotiff???
    #hydrostatic equilibtium with mean snow density and sea ice density
    rho_i = 882
    rho_w = 1025
    rho_s = 313

    #following Forsstrom et al, 2011, Annals of Glaciology
    fb = (ii - si * (rho_s/(rho_w-rho_i))) * (rho_w-rho_i)/rho_w
    x = range(0,len(fb))
       
    #cumulative distance allong the fixed date MP transect
    x = np.zeros_like(fb)
    x[1:] = np.cumsum(md)
    
    #extension at the FR transect
    if date!='20200305' and loc == 'ridgeFR1':
        x = x+19    #to have co-inciding crests

        
    #extension of the Allies ridge
    if loc == 'ridgeA1':
        if date=='20200117' or  date=='20200228' or date=='20200410':
            x = x+18


    #plot with equilibrium
    ax.plot(x,fb,label='ice surface',c='k',ls=':')
    
    #ax.plot(fb-ii,label='ice bottom'+date)
    #ax.plot(fb+si,label='snow surface'+date)
    ax.fill_between(x, fb, fb+si,alpha=.6, color=colors[1], label='snow')
    ax.fill_between(x, fb, fb-ii,alpha=.6, color=colors[0], label='ice')
    
    if loc == 'Nloop':
        ax.set_ylim(-8,1.8)
    elif loc == 'P4' or loc == 'P5':
        ax.set_ylim(-2,1)
    else:
        ax.set_ylim(-4,1.3)
    
    ax.set_xlim(0,x[-2])        #beacause last MP value/coordinate is typically same as first (at large distance)
    ax.legend(fontsize=25,loc='lower left',fancybox=True,facecolor=fig1.get_facecolor(),framealpha=.6)
    print(outname)
    fig1.savefig(outpath+outname,bbox_inches='tight', facecolor=fig1.get_facecolor(), edgecolor='none')
    exit()

    #save all these data and try to overlay them in a multi-profile plot
    fb_hat = savgol_filter(fb, window, polyorder) # window size 51, polynomial order 3
    ii_hat = savgol_filter(ii, window, polyorder)
    si_hat = savgol_filter(si, window, polyorder)  
    
    fb_list.append(fb_hat)
    ii_list.append(ii_hat) 
    si_list.append(si_hat)
    x_list.append(x)
    
fig2 = plt.figure(figsize=(20,10))
ax = fig2.add_subplot(111)
ax.set_xlabel('Length (m)', fontsize=20)
ax.set_title(title+'winter 2019/2020', fontsize=25)
ax.set_ylabel('Distance from water surface (m)', fontsize=20)
ax.tick_params(axis="x", labelsize=14)
ax.tick_params(axis="y", labelsize=14)
ax.set_facecolor('0.8')

for i in range(0,len(fb_list)):
    
    print(dates[i])
    
    #some bad ice data - dont plot:
    if dates[i]=='20191031' or dates[i]=='20191205' or dates[i]=='20200227' or dates[i]=='20200426':
    
        x=x_list[i]
        
        #use the same freeboard all the times
        #for a static feature e.g. cosolidating ridge, last measurement is best
        #for a deforming transect e.g. Nloop or Sloop each transect might be separate
        if loc == 'Sloop' or loc == 'Nloop':
            fb = fb_list[i]
        else:
            fb = fb_list[-1]
        
        #some (ridge) transects were getting longer (typically over level ice, so not much changes there...)
        if len(fb) < len(x):
            extra = len(x)-len(fb)
            fb = np.append(fb,fb_list[i][-extra:])
            
        #while some are getting shorter...
        if len(fb) > len(x):
            extra = len(fb)-len(x)
            fb = fb[:-extra]
        
        #ax.plot(x, fb,c='0.75')
        ax.plot(x, fb-ii_list[i],c=colors[i],label=datel[i]+' bottom')
        ax.plot(x, fb+si_list[i],c=colors[i])

x=x_list[-2]
ax.plot(x,fb,label='ice surface',c=colors[-1],ls=':')    
ax.fill_between(x, fb, fb+si_list[-2],alpha=1, color=colors[1], label='snow')
ax.fill_between(x, fb, fb-ii_list[-2],alpha=.3, color=colors[-1], label='ice')

    
#x=x_list[0]
#ax.plot(x,fb_list[0],label='ice surface',c='k')    

ax.set_ylim(-8,1.8)
if loc == 'ridgeA1':
    ax.set_ylim(-10.5,3)

if loc=='Sloop':
    ax.set_xlim(0,1500)
    ax.set_ylim(-4,1.8)
    
if loc=='Nloop':
    ax.set_xlim(0,1310)

#if loc=='special':
    #ax.set_ylim(-6,1.5)
    
#adding drill holes on the ridge
if 'ridge' in loc:
    ax.plot(x, fb-it2,c=colors[i],ls='--', label='bottom (diff. freq.)')
    ax.plot(x, fb-it3,c=colors[i],ls='--')
    ax.plot(x, fb-it4,c=colors[i],ls='--')
    ax.plot(x, fb-it5,c=colors[i],ls='--')
    ax.plot(x, fb-it6,c=colors[i],ls='--')
    ax.plot(x, fb-it7,c=colors[i],ls='--')
    ax.plot(x, fb-it8,c=colors[i],ls='--')
    ax.plot(x, fb-it9,c=colors[i],ls='--')
    ax.plot(x, fb-it10,c=colors[i],ls='--')
    
    
    
    if loc=='ridgeFR1':
        d=12
        dh1=.85
        ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'b', ls=':', label='drill hole 8/1/2020')
        #freeboard
        ax.plot(x[d], fb[d]-.09, 'x', c= 'r')
        #soft
        ax.plot([x[d],x[d]], [fb[d]-.7,fb[d]-.85], c= 'c', ls='-',lw=3)
        
        d=17
        dh1=6.05
        ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'b', ls=':')
        #freeboard
        ax.plot(x[d], fb[d]-.32, 'x', c= 'r',label='freeboard')
        #wet
        ax.plot([x[d],x[d]], [fb[d]-1.75,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7,label='wet')
        #voids
        ax.plot([x[d],x[d]], [fb[d]-1.65,fb[d]-1.75], c= 'salmon', ls='-',lw=5,label='void')
        ax.plot([x[d],x[d]], [fb[d]-2.1,fb[d]-2.15], c= 'salmon', ls='-',lw=5)
        ax.plot([x[d],x[d]], [fb[d]-2.35,fb[d]-2.4], c= 'salmon', ls='-',lw=5)
        ax.plot([x[d],x[d]], [fb[d]-3.25,fb[d]-3.3], c= 'salmon', ls='-',lw=5)
        ax.plot([x[d],x[d]], [fb[d]-4.15,fb[d]-4.2], c= 'salmon', ls='-',lw=5)
        #soft
        ax.plot([x[d],x[d]], [fb[d]-1.3,fb[d]-1.6], c= 'c', ls='-',lw=3,label='soft')
        ax.plot([x[d],x[d]], [fb[d]-2.45,fb[d]-3.15], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-3.3,fb[d]-4.15], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-4.45,fb[d]-6.], c= 'c', ls='-',lw=3)
        
        d=19
        dh1=7.1
        ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'b', ls=':')
        #freeboard
        #ax.plot(x[d], fb[d]-.09, 'x', c= 'r')
        #wet
        ax.plot([x[d],x[d]], [fb[d]-3.75,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7)
        #voids
        ax.plot([x[d],x[d]], [fb[d]-0.35,fb[d]-0.5], c= 'salmon', ls='-',lw=5)
        ax.plot([x[d],x[d]], [fb[d]-0.55,fb[d]-0.6], c= 'salmon', ls='-',lw=5)
        ax.plot([x[d],x[d]], [fb[d]-2.55,fb[d]-2.8], c= 'salmon', ls='-',lw=5)
        ax.plot([x[d],x[d]], [fb[d]-3.75,fb[d]-4.0], c= 'salmon', ls='-',lw=5)
        ax.plot([x[d],x[d]], [fb[d]-4.1,fb[d]-4.5], c= 'salmon', ls='-',lw=5)
        ax.plot([x[d],x[d]], [fb[d]-5,fb[d]-5.05], c= 'salmon', ls='-',lw=5)
        #soft
        ax.plot([x[d],x[d]], [fb[d]-1,fb[d]-1.1], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-2.05,fb[d]-2.55], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-3.,fb[d]-3.15], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-3.35,fb[d]-3.75], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-5.05,fb[d]-7.1], c= 'c', ls='-',lw=3)
        
        d=22
        dh1=6.1
        ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'b', ls=':')
        #wet
        ax.plot([x[d],x[d]], [fb[d]-2.3,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7)
        #voids
        ax.plot([x[d],x[d]], [fb[d]-0.4,fb[d]-0.5], c= 'salmon', ls='-',lw=5)
        ax.plot([x[d],x[d]], [fb[d]-1,fb[d]-1.15], c= 'salmon', ls='-',lw=5)
        ax.plot([x[d],x[d]], [fb[d]-2.7,fb[d]-2.8], c= 'salmon', ls='-',lw=5)
        ax.plot([x[d],x[d]], [fb[d]-4.2,fb[d]-4.25], c= 'salmon', ls='-',lw=5)
        #soft
        ax.plot([x[d],x[d]], [fb[d]-2.3,fb[d]-2.7], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-3,fb[d]-3.25], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-5,fb[d]-6], c= 'c', ls='-',lw=3)
        
        d=27
        dh1=4.1
        ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'b', ls=':')
        #freeboard
        ax.plot(x[d], fb[d]-.19, 'x', c= 'r')
        #wet
        ax.plot([x[d],x[d]], [fb[d]-1.2,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7)
        #voids
        ax.plot([x[d],x[d]], [fb[d]-0.4,fb[d]-0.5], c= 'salmon', ls='-',lw=5)
        ax.plot([x[d],x[d]], [fb[d]-2.35,fb[d]-3.8], c= 'salmon', ls='-',lw=5)
        #soft
        ax.plot([x[d],x[d]], [fb[d]-1.2,fb[d]-1.8], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-2.2,fb[d]-2.35], c= 'c', ls='-',lw=3)
        
        d=30
        dh1=4.05
        ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'b', ls=':')
        #wet
        ax.plot([x[d],x[d]], [fb[d]-1.25,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7)
        #voids
        ax.plot([x[d],x[d]], [fb[d]-1.65,fb[d]-1.67], c= 'salmon', ls='-',lw=5)
        ax.plot([x[d],x[d]], [fb[d]-3,fb[d]-3.1], c= 'salmon', ls='-',lw=5)
        #soft
        ax.plot([x[d],x[d]], [fb[d]-.25,fb[d]-.35], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-1.25,fb[d]-1.65], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-3.1,fb[d]-4.05], c= 'c', ls='-',lw=3)

    if loc=='ridgeFR2':
        d=24
        dh1=1.05
        ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'b', ls=':', label='drill hole 17/1/2020')
        #freeboard
        ax.plot(x[d], fb[d]-.05, 'x', c= 'r')
        
        d=34
        dh1=2.87
        ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'b', ls=':')
        #freeboard
        ax.plot(x[d], fb[d]-.29, 'x', c= 'r')
        
        d=39
        dh1=3.5
        ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'b', ls=':')
        #wet
        ax.plot([x[d],x[d]], [fb[d]-1.55,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7, label='wet')
        #void
        ax.plot([x[d],x[d]], [fb[d]-1.25,fb[d]-1.55], c= 'salmon', ls='-',lw=5, label='void')
        ax.plot([x[d],x[d]], [fb[d]-1.85,fb[d]-2.3], c= 'salmon', ls='-',lw=5)
        #soft
        ax.plot([x[d],x[d]], [fb[d]-1.55,fb[d]-1.85], c= 'c', ls='-',lw=3, label='soft')
        ax.plot([x[d],x[d]], [fb[d]-2.3,fb[d]-3.5], c= 'c', ls='-',lw=3)
        
        d=45
        dh1=4.3
        ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'b', ls=':')
        #wet
        ax.plot([x[d],x[d]], [fb[d]-1.3,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7)
        #void
        ax.plot([x[d],x[d]], [fb[d]-.1,fb[d]-.23], c= 'salmon', ls='-',lw=5)
        ax.plot([x[d],x[d]], [fb[d]-.43,fb[d]-.85], c= 'salmon', ls='-',lw=5)
        ax.plot([x[d],x[d]], [fb[d]-1,fb[d]-1.05], c= 'salmon', ls='-',lw=5)
        ax.plot([x[d],x[d]], [fb[d]-1.17,fb[d]-1.3], c= 'salmon', ls='-',lw=5)
        #soft
        ax.plot([x[d],x[d]], [fb[d]-1.3,fb[d]-4.3], c= 'c', ls='-',lw=3)
        
        d=47
        dh1=2.85
        ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'b', ls=':')
        #wet
        ax.plot([x[d],x[d]], [fb[d]-1.7,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7)
        #void
        ax.plot([x[d],x[d]], [fb[d]-1.7,fb[d]-1.75], c= 'salmon', ls='-',lw=5)
        ax.plot([x[d],x[d]], [fb[d]-2.45,fb[d]-2.55], c= 'salmon', ls='-',lw=5)
        #soft
        ax.plot([x[d],x[d]], [fb[d]-.75,fb[d]-1.7], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-1.75,fb[d]-2.45], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-2.55,fb[d]-2.85], c= 'c', ls='-',lw=3)
        
        d=56
        dh1=3.55
        ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'b', ls=':')
        #wet
        ax.plot([x[d],x[d]], [fb[d]-2.8,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7)
        #soft
        ax.plot([x[d],x[d]], [fb[d]-.2,fb[d]-2.8], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-2.8,fb[d]-3.55], c= 'c', ls='-',lw=3)
        
        d=63
        dh1=1.05
        ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'b', ls=':')
        #freeboard
        ax.plot(x[d], fb[d]-.13, 'x', c= 'r')
        #void
        ax.plot([x[d],x[d]], [fb[d]-.1,fb[d]-.18], c= 'salmon', ls='-',lw=5)
        #soft
        ax.plot([x[d],x[d]], [fb[d]-.55,fb[d]-1.05], c= 'c', ls='-',lw=3)

        d=41
        dh1=5.6
        ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'r', ls=':', label='drill hole 12/2/2020')
        #freeboard
        ax.plot(x[d], fb[d]-.45, 'x', c= 'r')
        #wet
        ax.plot([x[d],x[d]], [fb[d]-3,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7)
        #void
        ax.plot([x[d],x[d]], [fb[d]-.26,fb[d]-.3], c= 'salmon', ls='-',lw=5)
        ax.plot([x[d],x[d]], [fb[d]-.4,fb[d]-.45], c= 'salmon', ls='-',lw=5)
        ax.plot([x[d],x[d]], [fb[d]-.72,fb[d]-.75], c= 'salmon', ls='-',lw=5)
        ax.plot([x[d],x[d]], [fb[d]-2.42,fb[d]-4.5], c= 'salmon', ls='-',lw=5)
        #soft
        ax.plot([x[d],x[d]], [fb[d]-.22,fb[d]-.26], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-.3,fb[d]-.4], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-.45,fb[d]-.51], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-.68,fb[d]-.72], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-.75,fb[d]-1], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-1.25,fb[d]-2.42], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-4.5,fb[d]-5.6], c= 'c', ls='-',lw=3)
        
        d=51
        dh1=3.2
        ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'r', ls=':')
        #freeboard
        ax.plot(x[d], fb[d]-.13, 'x', c= 'r')
        #wet
        ax.plot([x[d],x[d]], [fb[d]-2.45,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7)
        #void
        ax.plot([x[d],x[d]], [fb[d]-.2,fb[d]-.25], c= 'salmon', ls='-',lw=5)
        #soft
        ax.plot([x[d],x[d]], [fb[d]-1.26,fb[d]-2], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-2.27,fb[d]-3.2], c= 'c', ls='-',lw=3)
        
    if loc=='ridgeFR3':
        d=10
        dh1=4.05
        ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'b', ls=':', label='drill hole 24/1/2020')
        #wet
        ax.plot([x[d],x[d]], [fb[d]-2.,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7, label='wet')
        #voids
        ax.plot([x[d],x[d]], [fb[d]-2,fb[d]-2.5], c= 'salmon', ls='-',lw=5, label='void')
        ax.plot([x[d],x[d]], [fb[d]-3.25,fb[d]-3.32], c= 'salmon', ls='-',lw=5)
        #soft
        ax.plot([x[d],x[d]], [fb[d]-1,fb[d]-2], c= 'c', ls='-',lw=3, label='soft')
        ax.plot([x[d],x[d]], [fb[d]-2.5,fb[d]-3.25], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-3.32,fb[d]-4.05], c= 'c', ls='-',lw=3)
        
        d=12
        dh1=5.15
        ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'b', ls=':')
        #wet
        ax.plot([x[d],x[d]], [fb[d]-2.3,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7)
        #voids
        ax.plot([x[d],x[d]], [fb[d]-.45,fb[d]-.5], c= 'salmon', ls='-',lw=5)
        ax.plot([x[d],x[d]], [fb[d]-3.5,fb[d]-3.57], c= 'salmon', ls='-',lw=5)
        ax.plot([x[d],x[d]], [fb[d]-3.65,fb[d]-3.75], c= 'salmon', ls='-',lw=5)
        ax.plot([x[d],x[d]], [fb[d]-3.85,fb[d]-3.9], c= 'salmon', ls='-',lw=5)
        #soft
        ax.plot([x[d],x[d]], [fb[d]-1.2,fb[d]-2.3], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-2.3,fb[d]-3.5], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-3.57,fb[d]-3.65], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-3.74,fb[d]-3.85], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-3.9,fb[d]-4.3], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-4.75,fb[d]-5.15], c= 'c', ls='-',lw=3)
        
        d=15
        dh1=5.75
        ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'b', ls=':')
        #wet
        ax.plot([x[d],x[d]], [fb[d]-3.7,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7)
        #voids
        ax.plot([x[d],x[d]], [fb[d]-.22,fb[d]-.41], c= 'salmon', ls='-',lw=5)
        ax.plot([x[d],x[d]], [fb[d]-1.25,fb[d]-1.28], c= 'salmon', ls='-',lw=5)
        ax.plot([x[d],x[d]], [fb[d]-2.6,fb[d]-2.61], c= 'salmon', ls='-',lw=5)
        #soft
        ax.plot([x[d],x[d]], [fb[d]-.41,fb[d]-1.25], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-1.28,fb[d]-1.35], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-2,fb[d]-2.6], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-2.62,fb[d]-5.75], c= 'c', ls='-',lw=3)
        
        d=20
        dh1=5.6
        ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'b', ls=':')
        #wet
        ax.plot([x[d],x[d]], [fb[d]-2.85,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7)
        #voids
        ax.plot([x[d],x[d]], [fb[d]-5.3,fb[d]-5.35], c= 'salmon', ls='-',lw=5)
        ax.plot([x[d],x[d]], [fb[d]-5.5,fb[d]-5.55], c= 'salmon', ls='-',lw=5)
        #soft
        ax.plot([x[d],x[d]], [fb[d]-1.75,fb[d]-4.4], c= 'c', ls='-',lw=3)
        
        d=25
        dh1=5.3
        ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'b', ls=':')
        #wet
        ax.plot([x[d],x[d]], [fb[d]-4,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7)
        #voids
        ax.plot([x[d],x[d]], [fb[d]-.3,fb[d]-.35], c= 'salmon', ls='-',lw=5)
        ax.plot([x[d],x[d]], [fb[d]-.9,fb[d]-.98], c= 'salmon', ls='-',lw=5)
        #soft
        ax.plot([x[d],x[d]], [fb[d]-.35,fb[d]-.9], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-4,fb[d]-5.3], c= 'c', ls='-',lw=3)

        d=9
        dh1=3.7
        ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'r', ls=':', label='drill hole 31/1/2020')
        #wet
        ax.plot([x[d],x[d]], [fb[d]-1.45,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7)
        #voids
        ax.plot([x[d],x[d]], [fb[d]-1.9,fb[d]-2.3], c= 'salmon', ls='-',lw=5)
        ax.plot([x[d],x[d]], [fb[d]-3.2,fb[d]-3.4], c= 'salmon', ls='-',lw=5)
        #soft
        ax.plot([x[d],x[d]], [fb[d]-1.45,fb[d]-1.8], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-2.3,fb[d]-2.55], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-3.65,fb[d]-3.7], c= 'c', ls='-',lw=3)
        
        d=11
        dh1=3.7
        ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'r', ls=':')
        #wet
        ax.plot([x[d],x[d]], [fb[d]-2.75,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7)
        #voids
        ax.plot([x[d],x[d]], [fb[d]-.5,fb[d]-.55], c= 'salmon', ls='-',lw=5)
        ax.plot([x[d],x[d]], [fb[d]-2.2,fb[d]-2.35], c= 'salmon', ls='-',lw=5)
        ax.plot([x[d],x[d]], [fb[d]-2.75,fb[d]-2.77], c= 'salmon', ls='-',lw=5)
        ax.plot([x[d],x[d]], [fb[d]-3.1,fb[d]-3.4], c= 'salmon', ls='-',lw=5)
        #soft
        ax.plot([x[d],x[d]], [fb[d]-2.15,fb[d]-2.2], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-2.35,fb[d]-2.4], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-3.4,fb[d]-3.7], c= 'c', ls='-',lw=3)
            
        d=14
        dh1=5.3
        ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'r', ls=':')
        #wet
        ax.plot([x[d],x[d]], [fb[d]-.85,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7)
        #voids
        ax.plot([x[d],x[d]], [fb[d]-.5,fb[d]-.52], c= 'salmon', ls='-',lw=5)
        ax.plot([x[d],x[d]], [fb[d]-.75,fb[d]-.85], c= 'salmon', ls='-',lw=5)
        ax.plot([x[d],x[d]], [fb[d]-1.1,fb[d]-1.15], c= 'salmon', ls='-',lw=5)
        #soft
        ax.plot([x[d],x[d]], [fb[d]-.65,fb[d]-.7], c= 'c', ls='-',lw=3)
        ax.plot([x[d],x[d]], [fb[d]-1.9,fb[d]-5.3], c= 'c', ls='-',lw=3)
        
        d=21
        dh1=5.4
        ax.plot([x[d],x[d]], [fb[d],fb[d]-dh1], 'o', c= 'r', ls=':')
        #wet
        ax.plot([x[d],x[d]], [fb[d]-3.7,fb[d]-dh1], 'x', c= 'b', ls=':',lw=7)
        #soft
        ax.plot([x[d],x[d]], [fb[d]-2.5,fb[d]-5.45], c= 'c', ls='-',lw=3)

    

ax.legend(fontsize=20,loc='lower left',fancybox=True,facecolor=colors[-1],framealpha=.1)
outname = loc+'_'+stp+'_profile_all_gridded.png'
fig2.savefig(outpath+outname,bbox_inches='tight')

#just snow
fig3 = plt.figure(figsize=(20,5))
ax = fig3.add_subplot(111)
ax.set_xlabel('Length (m)', fontsize=20)
ax.set_title(title+datel[-1], fontsize=25)
ax.set_ylabel('Distance from water surface (m)', fontsize=20)
ax.tick_params(axis="x", labelsize=14)
ax.tick_params(axis="y", labelsize=14)

for i in range(0,len(fb_list)-1):
    x=x_list[i]
    zero_level = np.zeros_like(x)
    
    #ax.plot(x, fb_list[i],c='0.75')
    ax.plot(x, zero_level+si_list[i],c=colors[i],label=datel[i]+' surface')

x=x_list[-1]
zero_level = np.zeros_like(x)
#ax.fill_between(x, fb_list[-1], fb_list[-1]-ii_list[-1],alpha=.3, color=colors[-1], label='ice')
ax.fill_between(x, zero_level, zero_level+si_list[-1],alpha=.3, color=colors[-2], label='snow')
    
#x=x_list[0]
#ax.plot(x,fb_list[0],label='ice surface',c='k')    
ax.set_ylim(0,1)
if loc=='Sloop':
    ax.set_xlim(0,1500)
if loc=='Nloop':
    ax.set_xlim(0,1310)
    
ax.legend(fontsize=20,loc='upper right',fancybox=True,facecolor=colors[-1],framealpha=.1)
outname = loc+'_profile_snow.png'
fig3.savefig(outpath+outname,bbox_inches='tight')

