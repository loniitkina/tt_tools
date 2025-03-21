import numpy as np
from glob import glob
from tt_func import getColumn, running_stats
from scipy.signal import savgol_filter
from datetime import datetime
import matplotlib.pyplot as plt

#comparisions of the total and consolidated thickness in old (Nloop) and (Sloop) ridges
#The difference between both thickness seems to depend on the ice temperature (so, also porosity). This is based on the observations of old ridges in Nloop
#Nloop spine can be traced to July, when it appears completelly consolidated, however the majority of other ridges in MeltMix is not fully consolidated

#check
#was there a different instrument used before December?: in processing 556 was used all the time until 20 July, then 512. Pontentialy this is not true. Yes, 51 was usd until the end of November (all noisy data) and then again on the last part of leg 4.
#High q channels are very noisy. 18khz q seems similar to i, should we use just 60kh q
#lowest I channel is also problematic
#what instrument was used in summer? In June there is a high spread. Low I are even lower than the rest. Channels are tight together in July.
#what is the max draft unde the Nloop on the multibeam??? 6-9 meters, but it doesnt go under the tallest sails.
#are the Nloop ridges too deep for this antenna? The data looks very unstable... It is OK after data that is not good for level ice neither was removed.
#add 20 July MeltMix
#reprocess the FR and AR from two frequencies and without negative values.
#check if FR3 has consistent voids in the drill holes (those that came through) about half meter above the bottom detected by multi-beam. This is very likley as hooks did not get through. How large are these voids? Could it be that EM does not detect any ice furthe down as there is enough salty water in the void?
#check Lange et al,  and Salganik et al, what kind of ridges doe they have...
#check drift speed from a buoy or floenavi, it seems like January was the slowest month with platelet ice occurence

#does rubble ice trap melt water from snow in June and freeze over. Was Poridge such rubble ice and not a real ridge?
#have high frequnecies larger footprint than the low ones?
#this data is complicated, wied and inconclusive. Likely complex timing and footprints. Maybe several waves of melt water etc...

#can we calculate sea ice growth by using SnowModel? If not, are there more complex physical models? Or are there only empirical ones?
#compare simulations of level ice and consolidated level growth, use snow depth (various standard deviations) and ocean heat fluxes until it fits

#What do the temperatures in the FR and AR show? Check Evgenii's paper.
#Salganik: there is no increase in conductive heat fluxes high up in the sail, just increased later heat flux deep inside the consolidation layer
#this is interpreted by snow slush. But what about melt of deep keel and transfer of melt water into the unconsolidated layer above???
#yes, Salganik says it is half by snow and half by keel melt - based on Allie's ridge. What if Nloop ridges there were different?
#Nloop ridge keels were largest end of January, decreased by half by end of February and were consolidated to 80% in March, afterwards it remained like that
#increase of mixing (drift speed) end of January? this causing melt of deep keels. There is more deep keels than open leads with snow removal. Plus snow gets trapped on level ice...

#summer melt and false bottoms: MeltMix shows consolidated layer deeper than total thickness end of June and then again 10 June. Between the layer disappears
#This could be related to the melt pond drainage and low drift speeds causing a persistent fresh layer, platelet ice and false bottoms under the ice (6-29 July) reported by Smith et al, 2022.

#Can we take all transects and make maps of consolidated and unconsolidated ridges in the CO?
#Use transects (also recon) that were used to Wenkai's paper + 2 MeltMix transects
#What can be the background - of course!!! Ship radar images!!!!
#Ridge is everything that is not level ice, ridges are classified in two categories
#Time series of consolidated and unconsolidated ridges

#Summary:
#Sloop: the ridge is consolidating, but the consolidation becomes slow as more snow accummulates, consolidation in Dec-Feb, no keel erosion. This ridge has a shalow keel and there is no erosion. It just fills in faster. Maybe platelet ice can only fill in by 80%?
#Nloop: thick snow, no consolidation until mid-Jan, then keel erosion simultaneously with snow erosion. Consolidation is completed by mid-March. mid-Jan to mid-March coincided exactly with the occurence of platelet ice at the same location!!!
#Sloop consolidation layer thickness is larger than in Nloop. In Nloop CC is same as level ice thickness. In Sloop this is a bit more. Likely the reason is snow depth.
#MeltMix: It looks like the Nloop ridge simply erodes to the consolidation layer. There are some consolidated and non-consolidated ridges, latter are likely younger, in July all are consolidated, consolidated and non-c ice thickness are close together (some nose, cc often more than tt), faster melt in keels than in level ice, despite melt ponds, fast snow melt, no further cosolidation with snow melt (vs Lange). Also in summer, consolidation is 100 to over 100%. This indicated non-conductive layer n top of the ice (e.g. general melt water). Lets look into some surface salinity data! There is more such stuff between the ridges than in the keels. Especially in June. The layer disappers. Then it appears again in July (melt water from melt ponds???)
#Webster: drainage channels appear end of June. End of July some ponds have no more bottom.
#timing, major consolidation in Sloop and Nloop happened during Jan/Feb, when air temperatures were coolest
#Salganik reports consolidation in April might be due to snow slush

#Hypothesis: there are new ridges being formed throuout the season. There are different mechanisms of how they consolidate, depending of when they are formed:
#1) by atmospheric cooling: freeze-up ridges like Nloop and Sloop
#2) by snow slush and keel melting: late winter after snow protects the keels from 1) What is platelet ice originated from keels??? This is suggested in their last sentence (Katlein et al). The strongest observations of platelets were between 15 Jan and 15 March. No platelets were found in level ice. Maybe all were swapped away into the ridges. Do we have any thin sections from the ridges? Do we have any cores left? Has anybody ever done any thin sections in the ridge??? What do we see in the CIRFA long core??? Platelats are rarely found in level ice (maybe Barneo 2016), and nobody makes thin sections of ridges. However, platelets are not consolidated. They need to freeze together.
#3) by snow melt water: during snow melt season
#Finally all MOSAiC ridges were FYI as there are no large ridges that survive the summer, just consolidated hummocks.

#Outlook
#The presented dataset is limited in space and time, but it could be used in data-model fusion like in Itkin and Liston, 2024.
#New model as the merge of Liston et al, 2018 and those used by Salganik should be used.
#The distribution of these processes in space and time should then be modeled - this will be our next paper.

#Conslusions:
#multifreqnecy EM based on EMPEX calibration from level ice, can detect ridge consolidation (time series of repeated surveys)
#can separate between consolidated and non-consolidated ridges (areal surveys can tell us which ridges are old and which are old)
#normally ridge study locations are selected based on the aperance of the sail, EM pre-survey is a better way.
#however, this is not a robust data as especially the extreme frequnecy data may give unrealistic values. Once this happens, the calibrations (performed survey-wise) fails and whole thick ice part of the survey is discarded. Most often is the data for mid-freqnwcise and level ice useful. We recommend using empirical curves (select one date in winter and one in melt period and plot for each frequency, with log scale, so that values for thick ice are visible, put into appendix?)
#during winter snow drives consolidations
#in summer no melt-snow-water consolidation observed in large ridges (vs following Lange), but maybe layer of fresh water detected in level ice that freezes later.
#in summer all unconsolidated ridges are in thinner FYI
#no deep keels survive summer, so all MOSAiC ridges were young (formed after freeze-up)
#modeling of consolidation requires still knowledge on X and Y.

##grid parameters
stp = '2'
#window size for savgol smoothing savgol_filter (must be odd and m.e. polyorder=3)
polyorder=3
window=21   #WARNING: use smoothing with caution :)
window=11
#window=5
##for point measurements (like ridges)
#polyorder=0
#window=1

#hydrostatic equilibrium with mean snow density and sea ice density
rho_i = 882
rho_w = 1025
rho_s = 313

#location and dates
#loc = 'Sloop'
#dates = ['20191205','20200102','20200109','20200220','20200227','20200305','20200330','20200426','20200507']
#title='Southern transect loop '

##ridge locations for each date - for visualization, it includes bits of level ice
#startx = [710, 700, 760, 700, 680, 720, 370, 380, 380]
#endx =   [1060,1050,1110,1050,1030,1070,720,730, 730]
#ridgeplot=True; ridgestats=False

##ridge locations for each date - for calculations, just ridge
#startx = np.array([710, 700, 760, 700, 680, 720, 370, 380, 380]) + 50
#endx =   np.array([1060,1050,1110,1050,1030,1070,720,730, 730]) - 50
#ridgeplot=False;ridgestats=True

###ridge locations for each date - for calculations, just crest
##startx = np.array([710, 700, 760, 700, 680, 720, 370, 380, 380]) + 100
##endx =   np.array([1060,1050,1110,1050,1030,1070,720,730, 730]) - 160

loc = 'Nloop'
dates = ['20191024','20191031','20191107','20191114','20191121','20191128','20191205', '20200102','20200109','20200130','20200220','20200305','20200320','20200403','20200424','20200430','20200507'] 
title='Northern transect loop '

#ridge locations for each date - for visulatization, two ridges
startx = [700,700,770,790, 770,700,700,770,790, 770,710,700,1040,770,720,745,730]
endx =   [920,920,990,1010,980,920,920,990,1010,980,930,920,1260,990,940,965,950]
ridgeplot=True; ridgestats=False

##ridge locations for each date - for calculations, left ridge
#startx = np.array([700,700,770,790, 770,710,700,1040,770,720,745,730]) + 15
#endx =   np.array([920,920,990,1010,980,930,920,1260,990,940,965,950]) - 140
#ridgeplot=False;ridgestats=True

#leg4 (Melinda used 20 July)
#loc = 'transect'
#dates = ['20200629','20200630','20200705','20200710','20200720']
#title = 'Melt Mix '

##ridge locations for each date - the three ridges, for visualization
#startx = [830, 850, 870, 840, 870]
#endx =   [1180,1200,1220,1190,1220]
#ridgeplot=True; ridgestats=False

##ridge locations for each date - just the left ridge of the Nloop, for calculations
#startx = np.array([830, 850, 870, 840, 870]) + 120
#endx =   np.array([1180,1200,1220,1190,1220]) - 135
#ridgeplot=False;ridgestats=True

####ridge locations for each date - the unconsolidated FYI rubble
##startx = [1400,1430,1475,1420,1360]
##endx =   [2000,2030,2075,2020,1960]

loc = 'ridgeD'
dates = ['20200410','20200416','20200424','20200430','20200507']
startx = [0, 0, 0, 0, 0]
endx =   [-1,-1,-1,-1,-1]
ridgeplot=True; ridgestats=False

dt = [ datetime.strptime(x, '%Y%m%d') for x in dates ]

import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
datel = [ datetime.strftime(x, '%b, %d %Y') for x in dt ]
print(datel)

print(loc)
#colors = plt.cm.rainbow(np.linspace(0, 1, len(dates)))
colors = plt.cm.Blues(np.linspace(0, 1, len(dates)))

if len(dates) == 1:
    colors = ['.1','.5']
    
#MOSAiC
inpath_table = '../data/ridges_multif/'
outpath = '../plots_ridges/'

fb_list=[]
si_list=[]
ii_list=[]
cc_list=[]
x_list=[]
modes_list=[]
si_mo_list=[]

for dd in range(0,len(dates)):
    date = dates[dd]
    print(date)

    outname = 'profile_'+date+'_'+loc+'gridded_lf.png'
    
    fname = inpath_table+'mosaic_gem-2+mp_'+date+'_'+loc+'_'+stp+'.csv'
    print(fname)
    
    #load data
    #Date,Lon,Lat,X,Y,Snow,f1525Hz_hcp_i,f1525Hz_hcp_q,f5325Hz_hcp_i,f5325Hz_hcp_q,18325Hz_hcp_i,f18325Hz_hcp_q,f63025Hz_hcp_i,f63025Hz_hcp_q,f93075Hz_hcp_i,f93075Hz_hcp_q
    mxx = np.array(getColumn(fname,3),dtype=np.float)
    myy = np.array(getColumn(fname,4),dtype=np.float)
    si = np.array(getColumn(fname,5),dtype=np.float)
    it1 = np.array(getColumn(fname,6),dtype=np.float)
    it2 = np.array(getColumn(fname,7),dtype=np.float)
    it3 = np.array(getColumn(fname,8),dtype=np.float)
    it4 = np.array(getColumn(fname,9),dtype=np.float)
    it5 = np.array(getColumn(fname,10),dtype=np.float)
    it6 = np.array(getColumn(fname,11),dtype=np.float)
    it7 = np.array(getColumn(fname,12),dtype=np.float)
    it8 = np.array(getColumn(fname,13),dtype=np.float)
    it9 = np.array(getColumn(fname,14),dtype=np.float)
    it10 = np.array(getColumn(fname,15),dtype=np.float)
    
    #ice thickness
    #ii = np.empty((3,len(it3)))
    #ii[0,:]=np.nan_to_num(it3, nan=-9999)
    #ii[1,:]=np.nan_to_num(it5, nan=-9999)
    #ii[2,:]=np.nan_to_num(it1, nan=-9999)
    #ii = np.mean(np.ma.array(ii,mask=ii<0),axis=0)
    
    ii = np.empty((2,len(it3)))
    ii[0,:]=np.nan_to_num(it3, nan=-9999)
    ii[1,:]=np.nan_to_num(it5, nan=-9999)
    ii = np.mean(np.ma.array(ii,mask=ii<0),axis=0)
            
    ##consolidated layer thickness
    #cc = np.empty((3,len(it3)))
    #cc[0,:]=np.nan_to_num(it6, nan=-9999)
    #cc[1,:]=np.nan_to_num(it8, nan=-9999)
    #cc[2,:]=np.nan_to_num(it10, nan=-9999)
    #cc = np.mean(np.ma.array(cc,mask=cc<0),axis=0)
    
    cc = np.empty((2,len(it3)))
    cc[0,:]=np.nan_to_num(it8, nan=-9999)
    cc[1,:]=np.nan_to_num(it10, nan=-9999)
    cc = np.mean(np.ma.array(cc,mask=cc<0),axis=0)
    
    #find mode of thickness = level ice thickness
    irbins = np.arange(0,2.5,.06)
    ii_pos = np.ma.array(it5,mask=it5==0);ii_pos=ii_pos.compressed()  #take only non-zero (not detected as negative) values
    hist = np.histogram(ii_pos,bins=irbins)
    srt = np.argsort(hist[0])                           #indexes that would sort the array
    mm = srt[-1]                                        #same as: np.argmax(hist[0])
    mm1 = np.argmax(hist[0])
    mo = (hist[1][mm] + hist[1][mm+1])/2           #take mean of the bin for the mode value
    #some ridges have very little ice, use max 1.7m thickness to contrain to level ice 
    #long transcts never have modal thickness over 1.7m
    if mo > 1.7:
        mo = np.mean(np.ma.array(ii_pos,mask=ii_pos>1.7))
    
    #snow depth on level ice 
    mask=it5>mo+.1
    si_mo = np.mean(np.ma.array(si,mask=mask))
    
    #get distances between fixed date MP points
    dx = mxx[1:]-mxx[:-1]
    dy = myy[1:]-myy[:-1]
    md = np.sqrt(dx**2+dy**2)
    #print(md)

    #plot
    fig1 = plt.figure(figsize=(20,10))
    #fig1 = plt.figure(figsize=(40,20))
    fig1.patch.set_facecolor('0.5')
    fig1.patch.set_facecolor('1')
    
    ax = fig1.add_subplot(111)
    ax.set_xlabel('Distance along transect (m)', fontsize=25)
    ax.set_title(title+datel[dd], fontsize=30, loc='left')
    ax.set_ylabel('Distance from water surface (m)', fontsize=25)
    ax.tick_params(axis="x", labelsize=24)
    ax.tick_params(axis="y", labelsize=24)
    ax.set_facecolor('0.8')
    #ax.set_facecolor('0.3')
    
    #surface elevation
    #following Forsstrom et al, 2011, Annals of Glaciology
    #fb = (ii - si * (rho_s/(rho_w-rho_i))) * (rho_w-rho_i)/rho_w
    fb = (ii * (rho_w-rho_i)/rho_w ) - (si * rho_s/rho_w)
    #print(fb)
    
    #cumulative distance allong the fixed date MP transect
    x = np.zeros_like(fb)
    x[1:] = np.cumsum(md)
    #print(x)

    #plot with equilibrium
    ax.plot(x,fb,label='ice surface',c='k',ls=':')
    ax.fill_between(x, fb, fb+si,alpha=.6, color=colors[1], label='snow')
    ax.fill_between(x, fb, fb-ii,alpha=.6, color=colors[0], label='ice')
    ax.fill_between(x, fb, fb-cc,alpha=.6, color=colors[0])
    
    ax.plot(x, fb-it1,'--w', label='1.5kHz i')
    ax.plot(x, fb-it2,'0.9',ls='--')
    ax.plot(x, fb-it3,'b',ls='--', label='5kHz i')
    ax.plot(x, fb-it4,'0.7',ls='--')
    ax.plot(x, fb-it5,'g',ls='--', label='18kHz i')
    ax.plot(x, fb-it6,'r',ls='--', label='18kHz q')
    ax.plot(x, fb-it7,'0.5',ls='--')
    ax.plot(x, fb-it8,'y',ls='--', label='60kHz q')
    ax.plot(x, fb-it9,'0.3',ls='--')
    ax.plot(x, fb-it10,'--k', label='98kHz q')
    
    ax.set_ylim(-6,1.8)
    
    ax.set_xlim(0,x[-2])        #beacause last MP value/coordinate is typically same as first (at large distance)
    ax.legend(fontsize=25,loc='lower left',fancybox=True,facecolor=fig1.get_facecolor(),framealpha=.6)
    #print(outname)
    #plt.show()
    fig1.savefig(outpath+outname,bbox_inches='tight', facecolor=fig1.get_facecolor(), edgecolor='none')

    #save all these data and try to overlay them in a multi-profile plot
    fb_hat = savgol_filter(fb, window, polyorder) # window size 51, polynomial order 3
    ii_hat = savgol_filter(ii, window, polyorder)
    cc_hat = savgol_filter(cc, window, polyorder)
    si_hat = savgol_filter(si, window, polyorder)  
    
    #print(np.ma.masked_invalid(si_hat).compressed().shape)

    fb_list.append(fb_hat)
    ii_list.append(ii_hat) 
    cc_list.append(cc_hat)
    si_list.append(si_hat)
    x_list.append(x)
    modes_list.append(mo)
    si_mo_list.append(si_mo)

#here plot just individual ridges and overlay
fig2 = plt.figure(figsize=(20,10))
ax = fig2.add_subplot(111)
ax.set_xlabel('Distance along transect (m)', fontsize=20)
ax.set_title(title+'ridge winter 2019/2020', fontsize=25)
ax.set_ylabel('Distance from water surface (m)', fontsize=20)
ax.tick_params(axis="x", labelsize=14)
ax.tick_params(axis="y", labelsize=14)
ax.set_facecolor('0.8')

mean_si_list=[]
mean_cc_list=[]
mean_ii_list=[]

for i in range(0,len(dates)):
    print(dates[i])
    
    si = np.argmin(abs(x_list[i]-startx[i]))
    ei = np.argmin(abs(x_list[i]-endx[i]))

    ax.plot(x_list[i][si:ei]-x_list[i][si], fb_list[i][si:ei]+si_list[i][si:ei],c=colors[i],label=datel[i])
    ax.plot(x_list[i][si:ei]-x_list[i][si], fb_list[i][si:ei]-ii_list[i][si:ei],c=colors[i])
    ax.plot(x_list[i][si:ei]-x_list[i][si], fb_list[i][si:ei]-cc_list[i][si:ei],c=colors[i],ls='--')
    
    #get means 
    si_mean = np.mean(si_list[i][si:ei]); mean_si_list.append(si_mean)
    cc_mean = np.mean(cc_list[i][si:ei]); mean_cc_list.append(cc_mean)
    ii_mean = np.mean(ii_list[i][si:ei]); mean_ii_list.append(ii_mean)
    
ax.plot(x_list[-1][si:ei]-x_list[i][si],fb_list[-1][si:ei],label='ice surface',c=colors[-1],ls=':')    
ax.fill_between(x_list[-1][si:ei]-x_list[i][si], fb_list[-1][si:ei], fb_list[-1][si:ei]+si_list[-1][si:ei],alpha=1, color=colors[1], label='snow')
ax.fill_between(x_list[-1][si:ei]-x_list[i][si], fb_list[-1][si:ei], fb_list[-1][si:ei]-cc_list[-1][si:ei],alpha=1, color=colors[-5], label='consolidated layer')
ax.fill_between(x_list[-1][si:ei]-x_list[i][si], fb_list[-1][si:ei], fb_list[-1][si:ei]-ii_list[-1][si:ei],alpha=.3, color=colors[-1], label='ice')

if ridgeplot==True:
    ax.legend(fontsize=20,loc='lower left',fancybox=True,facecolor=colors[-1],framealpha=.1)
    outname = loc+'_profile_all_gridded.png'
    fig2.savefig(outpath+outname,bbox_inches='tight')

ds = np.array(mean_si_list[1:]) - np.array(mean_si_list[:-1])
ratio = np.array(mean_cc_list) / np.array(mean_ii_list)
dr = ratio[1:]-ratio[:-1]

fig3 = plt.figure(figsize=(10,10))
bx = fig3.add_subplot(111)

bx.plot(dt,mean_si_list,'o',label='snow depth')
bx.plot(dt,ratio,'.',label='consolidation')

bx.plot(dt[1:],ds,'s',label='snow erosion/deposition')
bx.plot(dt[1:],dr,'x',label='consolidation change')    

bx.plot(dt,modes_list,'o',label='mode')
bx.plot(dt,si_mo_list,'s',label='level ice snow')

#x=ds 
#y=dr
#model = np.polyfit(x, y, 1)
#print('coefficients: ', model)

#predict = np.poly1d(model)
#from sklearn.metrics import r2_score
#r2 = r2_score(y, predict(x))
#print('R2: ',r2)

#bx.text(.8, .1, '$R^2$= '+str(np.round(r2,2)), ha="left", va="center", size=20, transform=bx.transAxes)
bx.legend()

plt.show()

if ridgestats==True:
    #save the data in file
    file_name = inpath_table+loc+'_cc.csv'
    print(file_name)

    tt = [dt,mean_si_list,mean_ii_list,mean_cc_list,modes_list,si_mo_list]
    table = list(zip(*tt))

    with open(file_name, 'wb') as f:
        #header
        f.write(b'date,mean ridge snow depth,mean ridge ice thickness,mean consolidated layer thickness,modal thickness,level ice snow depth\n')
        np.savetxt(f, table, fmt="%s", delimiter=",")

