import csv
import re
import numpy as np
from glob import glob
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from tt_func import getColumn

#TODO redo the low runs with the correct input files. The model simulations and obs should fit just like for the 'normal'

inpath='../data/SnowModel/final/'
#inpath_obs = '../data/MCS/MP/SnowModel_calval/'
inpath_obs = '../../snow_model/mosaic_ship_2023/'
outpath='../plots_sm/'

locs = ['Nloop','Sloop','Runwy']
melt_limit = [25,18,4]
cols = ['royalblue','purple','teal','c']
#atext = ['a) Deformed SYI','b) Ponded SYI','c) Level FYI']
atext = ['a','b','c']

numdays=366*8
start = datetime(2019,8,1)
dt = [start + timedelta(hours=x*3) for x in range(numdays)]
end = datetime(2020,8,1)

fig1 = plt.figure(figsize=(10,20))
ax = fig1.add_subplot(311)
bx = fig1.add_subplot(312)
cx = fig1.add_subplot(313)

plots = [ax,bx,cx]

#start the scatter plot
fig2 = plt.figure(figsize=(10,10))
px = fig2.add_subplot(111)
x=[]
y=[]

for i in range(0,len(locs)):
    loc = locs[i]

    #name_date='2023_06_28'
    name_date='2024_04_08'
    name_date='2024_05_15'
    name_date='2024_07_17'

    fname_normal = inpath+'snow_tice_'+loc+'_'+name_date+'_normal.dat'
    fname_level = inpath+'snow_tice_'+loc+'_'+name_date+'_level.dat'
    fname_level_low = inpath+'snow_tice_'+loc+'_'+name_date+'_level_low.dat'
    
    print(fname_normal)
    #HEADER
    #iter,swed_mod1,swed_mod2,snod,sden,dyn_corr,tice,swed_obs,sden_obs,snod_obs,timo_obs
    
    results = csv.reader(open(fname_normal))
    #get rid of all multi-white spaces and split in those that remain
    results_clean = [re.sub(" +", " ",row[0]) for row in results]

    snod = [row.split(" ")[4] for row in results_clean]
    snod = np.array(snod,dtype=np.float)     
    snod = np.ma.array(snod,mask=snod==-9999)
    
    ##original model data before dynamic correction and density assimilation
    #swe_mod1 = [row.split(" ")[2] for row in results_clean]
    #swe_mod1 = np.array(swe_mod1,dtype=np.float)     
    #swe_mod1 = np.ma.array(swe_mod1,mask=snod==-9999)
    #sden = [row.split(" ")[5] for row in results_clean]
    #sden = np.array(sden,dtype=np.float)     
    #sden = np.ma.array(sden,mask=snod==-9999)
    #snod = swe_mod1*1000/sden
    
    swe_mod2 = [row.split(" ")[2] for row in results_clean]
    swe_mod2 = np.array(swe_mod2,dtype=np.float)     
    swe_mod2 = np.ma.array(swe_mod2,mask=snod==-9999)
    
    tice = [row.split(" ")[7] for row in results_clean]
    tice = np.array(tice,dtype=np.float)     
    tice = np.ma.array(tice,mask=tice==-9999)
    
    #so = [row.split(" ")[10] for row in results_clean]
    #so = np.array(so,dtype=np.float)     
    #so = np.ma.array(so,mask=so==-9999).compressed()
    #print(so)
    
    #get snow depth standard deviations from observations (not stored in model output)
    if loc=='Runwy': loc='runway'
    of = glob(inpath_obs+'*_low/1_sm/3_snow_obs/1_orig/ts_'+loc+'_1m_gridded_melt_swe_level.csv')[0]
    print(of)
    if loc=='runway': loc='Runwy'
    
    year = getColumn(of,0); month = getColumn(of,1); day = getColumn(of,2);
    dt_o = [ datetime(int(year[x]),int(month[x]),int(day[x])) for x in range(0,len(year)) ]
    
    so = getColumn(of,3);so = np.array(so,dtype=np.float)
    #print(so); exit()
    #do = getColumn(of,8);do = np.array(do,dtype=np.float)
    #sweo = getColumn(of,9);sweo = np.array(sweo,dtype=np.float)
    #so = sweo*1000/do
    #print(so)
    
    so_sd = getColumn(of,4);so_sd = np.array(so_sd,dtype=np.float) 
    io_m = getColumn(of,5);io_m = np.array(io_m,dtype=np.float)*-1
    io_sd = getColumn(of,6);io_sd = np.array(io_sd,dtype=np.float)
    
    #other relevant results - level ice
    results1 = csv.reader(open(fname_level))
    results_clean1 = [re.sub(" +", " ",row[0]) for row in results1]
    
    snod1 = [row.split(" ")[4] for row in results_clean1]
    snod1 = np.array(snod1,dtype=np.float)     
    snod1 = np.ma.array(snod1,mask=snod1==-9999)
    
    tice1 = [row.split(" ")[7] for row in results_clean1]
    tice1 = np.array(tice1,dtype=np.float)     
    tice1 = np.ma.array(tice1,mask=tice1==-9999)
    
    #other relevant results - level ice low 
    results = csv.reader(open(fname_level_low))
    results_clean = [re.sub(" +", " ",row[0]) for row in results]
    
    tice_ll = [row.split(" ")[7] for row in results_clean]
    tice_ll = np.array(tice_ll,dtype=np.float)     
    tice_ll = np.ma.array(tice_ll,mask=tice_ll==-9999)
        
    snod_ll = [row.split(" ")[4] for row in results_clean]
    snod_ll = np.array(snod_ll,dtype=np.float)     
    snod_ll = np.ma.array(snod_ll,mask=snod_ll==-9999)
    
    #scatter plot of sea ice modes
    mod = [row.split(" ")[11] for row in results_clean]
    mod = np.array(mod,dtype=np.float)
    mask=(mod==-9999) | (mod<-2)
    mod_o = np.ma.array(mod,mask=mask).compressed()
    mod_m = np.ma.array(tice_ll,mask=mask).compressed()
    dt_mod = np.ma.array(dt,mask=mask).compressed()
    
    #some modes are not detected right. Inspection of the profiels suggested the following corrections:
    if loc=='Sloop':
        #print(mod_o)
        mod_o[4]=-.8
        mod_o[17]=-1.71
        #print(mod_o)
        #exit()
    if loc=='Runwy':
        #print(mod_o)
        mod_o[1]=-1.11
        mod_o[3]=-1.41
        #print(mod_o)
        #exit()   
        loc = 'Runway'
        
    px.plot(mod_o[1:melt_limit[i]],mod_m[1:melt_limit[i]],'X', markeredgewidth=3, ms=15, mec=cols[i], c='gold', label=loc)
    if loc=='Nloop':
        px.plot(mod_o[melt_limit[i]:],mod_m[melt_limit[i]:],'X', markeredgewidth=3, ms=15, mec='grey', c='gold', label='Melt Mix')
    y.extend(mod_m[1:melt_limit[i]])
    x.extend(mod_o[1:melt_limit[i]])

    #plotting
    #interface
    plots[i].plot(dt,np.zeros_like(snod),':k')
    #model snow
    plots[i].plot(dt,snod*4, lw=2, ls='--', c=cols[i], label='mean')
    plots[i].plot(dt,snod1*4, lw=2, ls=':', c=cols[i], label='level')
    plots[i].plot(dt,snod_ll*4, lw=2, ls='-', c=cols[i], label='level$-\sigma$')
    #model ice
    plots[i].plot(dt,tice, lw=2, ls='--', c=cols[i])
    plots[i].plot(dt,tice1, lw=2, ls=':', c=cols[i])
    plots[i].plot(dt,tice_ll, lw=2, ls='-', c=cols[i])
    #observations snow
    #do not plot the melt period     
    plots[i].errorbar(dt_o[:-23],so[:-23]*4,so_sd[:-23]*4,ls='None',marker='x', markeredgewidth=3, markersize=8, c=cols[i], label=loc)
    #plots[i].plot(dt_o[:-23],so[:-23]*4,ls='None',marker='x', markeredgewidth=3, markersize=8, c=cols[i], label=loc)
    #observations ice
    plots[i].plot(dt_mod[1:melt_limit[i]],mod_o[1:melt_limit[i]],'x', markeredgewidth=3, c=cols[i], ms=8)
    mod_o_err = np.ones_like(mod_o)*.1
    #plots[i].errorbar(dt_mod[:melt_limit[i]],mod_o[:melt_limit[i]],mod_o_err[:-23],ls='None',marker='x', markeredgewidth=2, markersize=8, c=cols[i])
    plots[i].fill_between(dt_mod[1:melt_limit[i]],mod_o[1:melt_limit[i]], mod_o[1:melt_limit[i]]+mod_o_err[1:melt_limit[i]], color='0.8')
    plots[i].fill_between(dt_mod[1:melt_limit[i]],mod_o[1:melt_limit[i]], mod_o[1:melt_limit[i]]-mod_o_err[1:melt_limit[i]], color='0.8')
    #plots[i].errorbar(dt_o[:-12],io_m[:-12],io_sd[:-12],ls='None',marker='x', markeredgewidth=2, markersize=8, c=cols[i])
    
    #different color for the melt period
    #dont plot the last snow - it is just SSL
    plots[i].errorbar(dt_o[-23:-10],so[-23:-10]*4,so_sd[-23:-10]*4,ls='None',marker='x', markeredgewidth=1, markersize=8, c='grey', label='Melt Mix')
    plots[i].plot(dt_mod[melt_limit[i]:],mod_o[melt_limit[i]:],'x', markeredgewidth=1, c='grey', ms=8)

    print('get max snow depth value and date')
    print('**********************',loc)
    print(np.max(snod))
    print(dt[np.argmax(snod)])

    print('get max SWE value and date')
    print(np.max(swe_mod2))
    print(dt[np.argmax(swe_mod2)])

    print('get max sea ice thickness and date')
    print(np.min(tice_ll))
    print(dt[np.argmin(tice_ll)])




        
#plot the Stakes data - pick FYI stakes that are simlar to Runway transect. Ridge Ranch are FYI, but largely influced by a ridge drift
#No SYI stakes survived into CO2.
stakes_names = ['Runaway Stakes/dart_stakes_clu_7','Ridge Ranch/dart_stakes_clu_6']
#stakes_names = ['Runaway Stakes/dart_stakes_clu_7']
fname_stakes = '../data/stakes/resource_map_doi_10_18739_A2NK36626/data/home/visitor/Raphael/ablationStakes_thicknessGauge_archive/ablationStakes_hotwireThicknessGauges_MOSAiC.csv'
print(fname_stakes)

#Site name,Stake ID,Ice age,Date installed,Date of last measurement,Initial ice thickness (cm),Initial draft (cm),Measurement date,Snow surface measurement (cm),Snow surf
#ace measurement (normalized) (cm),Ice surface measurement (cm),Ice surface measurement (normalized) (cm),Ice surface QC flag,Ice bottom measurement (cm),Ice bottom measu
#rement (normalized) (cm),Ice bottom QC flag,Snow depth (calculated) (cm),Pond depth (cm),Pond flag,Ice thickness (calculated) (cm),Drilled ice thickness (cm),Comments

stakes_name = getColumn(fname_stakes,0)
dates = getColumn(fname_stakes,7)
dt = [ datetime.strptime(x, '%Y.%m.%d') for x in dates ]
snod = getColumn(fname_stakes,16);snod = np.array(snod,dtype=np.float)/100
it = getColumn(fname_stakes,19);it = np.array(it,dtype=np.float)/100 *-1
stakes_name = getColumn(fname_stakes,0)

c=['y','b']
    
for nn in range(0,len(stakes_names)):
    name = stakes_names[nn]
    #print(name)
    mask = [ x==name for x in stakes_name ]
    mask = np.array(mask)
    
    dt_name = np.ma.array(dt,mask=~mask).compressed()
    it_name = np.ma.array(it,mask=~mask).compressed()
    snod_name = np.ma.array(snod,mask=~mask).compressed()

    label=name.split('/')[0]
    if label=='Runaway Stakes': label='RunAway'
       
    #the measurements/dates are not sorted
    #import to pandas, sort and make means and SD per measurement date
    dt_sorted,idx = np.unique(dt_name,return_inverse=True)
    
    snod_mean = np.zeros_like(dt_sorted)
    snod_std = np.zeros_like(dt_sorted)
    it_mean = np.zeros_like(dt_sorted)
    it_std = np.zeros_like(dt_sorted)
    for ii in range(0,len(dt_sorted)):
        mask_id = dt_name==dt_sorted[ii]
        
        ss=np.ma.array(snod_name,mask=~mask_id).compressed()
        snod_mean[ii] = np.mean(ss)
        snod_std[ii] = np.std(ss)
        
        tt=np.ma.array(it_name,mask=~mask_id).compressed()
        tt=np.ma.masked_invalid(tt)
        
        it_mean[ii] = np.mean(tt)
        it_std[ii] = np.std(tt)

    cx.errorbar(dt_sorted,snod_mean*4,snod_std,marker='X', c=c[nn],ls='None',label=label)
    cx.errorbar(dt_sorted,it_mean,it_std,marker='X', c=c[nn],ls='None')
        
    ##write this into a file
    #tt = [dt_sorted,snod_mean,snod_std,it_mean,it_std,it_mean,snod_mean,snod_std,snod_mean,snod_std]
    #table = list(zip(*tt))

    #file_ts = inpath_obs+'ts_'+label.split(' ')[0]+'.csv'

    #print(file_ts)
    #with open(file_ts, 'wb') as f:
        ##header
        #f.write(b'Date/Time, snow depth mean, snow depth SD, ice thickness mean, ice thickness SD, ice thickness mode, snow depth on level ice (mode+-10cm), snow depth on level ice STD, snow depth in deformed ice, snow depth on deformed ice STD\n')
        #np.savetxt(f, table, fmt="%s", delimiter=",")

#plot the coring data
#for FYI deformed: maybe we can extrapolate to Sloop last measurement in the ridges - based on what we saw on initial survay in July!
fnames = ['FYI_snow_clean.csv',
          'SYI_snow_clean.csv']
inpath_coring = '../data/coring_dark_site_Evgenii/'

for fn in fnames:
    fname = glob(inpath_coring+fn)[0]
    #print(fname)

    #b'date,snow depth (m),snow depth std (m),ice thickness (m),ice thickness std (m),ice mode (m)\n'
    dates = getColumn(fname,10)
    dt = [ datetime.strptime(x, '%Y/%m/%d %H:%M') for x in dates ]
    snod = getColumn(fname,1);snod = np.array(snod,dtype=np.float)/100
    it = getColumn(fname,8);it = np.array(it,dtype=np.float)/100 *-1
    it_sd = getColumn(fname,9);it_sd = np.array(it_sd,dtype=np.float)/100
    #print(it_sd)
    
    age=fn.split('_')[0]
    
    if age=='FYI':
        c='lime'
        cx.plot(dt[:-3],snod[:-3]*4,'X', c=c,label='Coring '+age)   #last 3 measurements are SSL
        cx.errorbar(dt,it,it_sd,marker='X',ls='None', c=c)
        
    else:
        c='r'
        ax.plot(dt[:-2],snod[:-2]*4,'X', c=c,label='Coring '+age)   #last 2 measurements are SSL
        ax.errorbar(dt,it,it_sd,marker='X',ls='None', c=c)

ax.set_ylabel('Ice thickness/Snow depth (m)',fontsize=20) # Y axis data label
bx.set_ylabel('Ice thickness/Snow depth (m)',fontsize=20)
cx.set_ylabel('Ice thickness/Snow depth (m)',fontsize=20)

#make scatter plot for all the ice thickness
for p in range(0,len(plots)):
                   
    i = plots[p]
    
    #fix the snow ticks
    i.set_ylim(-2.1,2.2)
    i.set_yticks([-2,-1,0,1,2])
    i.set_yticklabels([-2,-1,0,0.25,.5])
    
    i.tick_params(axis="x", labelsize=14)
    i.tick_params(axis="y", labelsize=14)

    i.set_xlim(datetime(2019,8,18),datetime(2020,8,1))

    # Put a legend below current axis
    i.legend(loc='upper left',
            shadow=False, ncol=2, fontsize=13, frameon=False)
    
    #annotate
    i.text(datetime(2019,9,1),-1.75,atext[p],size=20)

for ip in [ax,bx,cx]:
    ip.axvspan(datetime(2019,10,16), datetime(2019,11,1),color='royalblue',alpha=.2)    #Fort Ridge formation
    ip.axvspan(datetime(2019,11,14), datetime(2019,12,5),color='gold',alpha=.2)         #November shear zone
    ip.axvspan(datetime(2020,1,22), datetime(2020,2,7),color='pink',alpha=.2)         #Jan/Feb lead
    ip.axvspan(datetime(2020,3,15), datetime(2020,4,30),color='limegreen',alpha=.1)     #March-April deformation


fig1.autofmt_xdate()
#plt.show()
fig1.savefig(outpath+'sm_season_MOSAiC',bbox_inches='tight')
exit()

#finish the scatterplot
#print(x)
#print(y)
model = np.polyfit(x, y, 1)
print('coefficients: ', model)

predict = np.poly1d(model)
from sklearn.metrics import r2_score
r2 = r2_score(y, predict(x))
print('R2: ',r2)

x_lin_reg = np.arange(-2, -.2,.1)
y_lin_reg = predict(x_lin_reg)

#print(x_lin_reg)
#print(y_lin_reg)

px.plot(x_lin_reg, y_lin_reg, c='r')#, label=datel[dd])

#get siginificance
from scipy.stats import linregress

#print(linregress(x,y))
slope,intercept,rvalue,pvalue,stderr=linregress(x,y)
#p-value : two-sided p-value for a hypothesis test whose null hypothesis is that the slope is zero
if pvalue < 0.01:   #significant at 99%
    print('significant!')

#for just Nloop
px.text(-1.8, -.5, '$R^2$= '+str(np.round(r2,2)), ha="left", va="center", size=20)
px.text(-1.8, -.6, '$N$= '+str(np.round(len(x),2)), ha="left", va="center", size=20)
px.text(-1.8, -.7, '$p$= '+str(np.round(pvalue,5)), ha="left", va="center", size=20)  

px.set_ylabel('Ice thickness model (m)',fontsize=20)
px.set_xlabel('Ice thickness transect (m)',fontsize=20)
px.set_xlim(-1.9,-.3)
px.set_ylim(-1.9,-.3)

px.tick_params(axis="x", labelsize=14)
px.tick_params(axis="y", labelsize=14)

px.legend(loc='lower right',
            shadow=False, ncol=1, fontsize=20, frameon=False)
#plt.show()
fig2.savefig(outpath+'sm_it_mod'+loc,bbox_inches='tight')
