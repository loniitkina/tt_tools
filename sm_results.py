import csv
import re
import numpy as np
from glob import glob
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from tt_func import getColumn

#TODO: plot normal snow depth, standard deviations, then level ice snow depth and standard deviations
#do not plot level minus 1 SD snow depth


inpath='../data/SnowModel/final/'
inpath_obs = '../data/MCS/MP/SnowModel_calval/'
outpath='../plots_sm/'

locs = ['Nloop']#,'Sloop','Runwy']
#locs = ['Runwy']
ls = ['-','--',':','-']
cols = ['royalblue','purple','teal','c']

numdays=366*8
start = datetime(2019,8,1)
dt = [start + timedelta(hours=x*3) for x in range(numdays)]
end = datetime(2020,8,1)

fig1 = plt.figure(figsize=(20,10))
ax = fig1.add_subplot(111)

for i in range(0,len(locs)):
    loc = locs[i]

    fname_normal = inpath+'snow_tice_'+loc+'_2023_06_28_normal.dat'
    
    
    
    fname_level = inpath+'snow_tice_'+loc+'_2023_06_28_level.dat'
    fname_level_low = inpath+'snow_tice_'+loc+'_2023_06_28_level_low.dat'
    
    fname_level_low = inpath+'snow_tice_'+loc+'_2023_07_06_test1.dat'   #level, macf+0.2
    fname_level_low = inpath+'snow_tice_'+loc+'_2023_07_06_test2.dat'   #level, rks=macf+(0.5*macf)
    
    #plt.grid()
    
    print(fname_normal)
    #HEADER
    #iter,swed_mod1,swed_mod2,snod,sden,dyn_corr,tice,swed_obs,sden_obs,snod_obs,timo_obs
    
    results = csv.reader(open(fname_normal))
    #get rid of all multi-white spaces and split in those that remain
    results_clean = [re.sub(" +", " ",row[0]) for row in results]

    snod = [row.split(" ")[4] for row in results_clean]
    snod = np.array(snod,dtype=np.float)     
    snod = np.ma.array(snod,mask=snod==-9999)
    
    so = [row.split(" ")[10] for row in results_clean]
    so = np.array(so,dtype=np.float)
    mask_o = so==-9999
    so = np.ma.array(so,mask=mask_o)
    
    #recalculate snow depth - yes, problem solved the SWE and snow depth in SnowModel input file were not coinciding!!!
    do = [row.split(" ")[9] for row in results_clean]; do = np.array(do,dtype=np.float)
    sweo = [row.split(" ")[8] for row in results_clean]; sweo = np.array(sweo,dtype=np.float)
    do = np.ma.array(do,mask=mask_o)
    sweo = np.ma.array(sweo,mask=mask_o)
    
    so = sweo*1000/do
    
    ##
    #io = [row.split(" ")[11] for row in results_clean]
    #io = np.array(io,dtype=np.float)     
    #io = np.ma.array(io,mask=io==-9999)
    
    dt_o = np.ma.array(dt,mask=mask_o).compressed()
    so = so.compressed()
    
    #also get the standard deviations from the observations
    if loc=='Runwy':
        loc='runway'
    of = glob(inpath_obs+'ts_'+loc+'_1m_gridded_melt_swe_normal.csv')[0]
    print(of)
    so_sd = getColumn(of,4)[:len(so)];so_sd = np.array(so_sd,dtype=np.float) 
    io_mod = getColumn(of,7)[:len(so)];io_mod = np.array(io_mod,dtype=np.float)*-1
    io_m = getColumn(of,5)[:len(so)];io_m = np.array(io_m,dtype=np.float)*-1
    io_sd = getColumn(of,6)[:len(so)];io_sd = np.array(io_sd,dtype=np.float)
    
    #ice mode observations have some outliers
    io_mod = np.ma.array(io_mod,mask=io_mod<-2)
    
    results = csv.reader(open(fname_level_low))
    #get rid of all multi-white spaces and split in those that remain
    results_clean = [re.sub(" +", " ",row[0]) for row in results]
    
    tice = [row.split(" ")[7] for row in results_clean]
    tice = np.array(tice,dtype=np.float)     
    tice = np.ma.array(tice,mask=tice==-9999)
    
    snod_ll = [row.split(" ")[4] for row in results_clean]
    snod_ll = np.array(snod_ll,dtype=np.float)     
    snod_ll = np.ma.array(snod_ll,mask=snod_ll==-9999)

    if loc=='Nloop':
        ax.plot(dt,snod, lw=3, ls=ls[i], c='turquoise', label='SnowModel snow')
        ax.plot(dt,snod_ll, lw=1, ls=ls[i], c='turquoise')

        ax.plot(dt,np.zeros_like(snod),':k')
        
        ax.plot(dt,tice, lw=3, ls=ls[i], c='cornflowerblue', label='HIGHTSI sea ice')
        
    else:
        ax.plot(dt,snod, lw=3, ls=ls[i], c='turquoise')
        ax.plot(dt,snod_ll, lw=1, ls=ls[i], c='turquoise')
        
        ax.plot(dt,np.zeros_like(snod),':k')
        
        ax.plot(dt,tice, lw=3, ls=ls[i], c='cornflowerblue')
    
    #different color for the melt period
    if loc=='Nloop':
        ax.errorbar(dt_o,so,so_sd,ls='None',marker='x', markeredgewidth=3, markersize=8, c=cols[i], label='Transect '+loc)
        
        #from SnowModel output
        #ax.plot(dt,io,'x', markeredgewidth=3, c=cols[i], ms=8)
        #from SnowModel input (whole loop)  - should be the same as above
        ax.plot(dt_o,io_mod,'x', markeredgewidth=3, c=cols[i], ms=8)
        
        #use different color for the melt period
        ax.errorbar(dt_o[-11:],so[-11:],so_sd[-11:],ls='None',marker='x', markeredgewidth=2, markersize=8, c='grey', label='Mixed type')
        ax.plot(dt_o[-11:],io_mod[-11:],'x', markeredgewidth=3, c='grey', ms=8)
        
    else:
        #do not plot the melt period
        ax.errorbar(dt_o[:-12],so[:-12],so_sd[:-12],ls='None',marker='x', markeredgewidth=2, markersize=8, c=cols[i], label='Transect '+loc)

    
        ax.plot(dt_o[:-12],io_mod[:-12],'x', markeredgewidth=3, c=cols[i], ms=8)

##plot the coring data
##for FYI deformed: maybe we can extrapolate to Sloop last measurement in the ridges - based on what we saw on initial survay in July!
#fnames = ['FYI_snow_clean.csv',
          #'SYI_snow_clean.csv']
#inpath_coring = '../data/coring_dark_site_Evgenii/'

#for fn in fnames:
    #fname = glob(inpath_coring+fn)[0]
    #print(fname)

    ##b'date,snow depth (m),snow depth std (m),ice thickness (m),ice thickness std (m),ice mode (m)\n'

    #dates = getColumn(fname,10)
    #dt = [ datetime.strptime(x, '%Y/%m/%d %H:%M') for x in dates ]
    #snod = getColumn(fname,1);snod = np.array(snod,dtype=np.float)/100
    #it = getColumn(fname,8);it = np.array(it,dtype=np.float)/100 *-1
    #it_sd = getColumn(fname,9);it_sd = np.array(it_sd,dtype=np.float)/100
    
    
    #print(it_sd)
    

    #age=fn.split('_')[0]
    
    #if age=='FYI':
        #c='r'
    #else:
        #c='g'

    #ax.plot(dt,snod,'.', c=c,label='coring '+age)
    ##if age=='SYI':
    ##ax.errorbar(dt[:-5],it[:-5],it_sd[:-5],marker='.',ls='None', c=c)    #last SYI corings are from different site (CO2)
    ##else:
    #ax.errorbar(dt,it,it_sd,marker='.',ls='None', c=c)

#plot the Stakes data - pick FYI stakes that are simlar to Runway transect. Ridge Ranch are FYI, but largely influced by a ridge drift
#No SYI stakes survived into CO2.
stakes_names = ['Runaway Stakes/dart_stakes_clu_7','Ridge Ranch/dart_stakes_clu_6']
stakes_names = ['Runaway Stakes/dart_stakes_clu_7']
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
    print(name)
    #print(stakes_name)
    mask = [ x==name for x in stakes_name ]
    mask = np.array(mask)
    #mask = np.where(mask==True,1,0)
    #print(mask)
    #exit()
    
    dt_name = np.ma.array(dt,mask=~mask).compressed()
    it_name = np.ma.array(it,mask=~mask).compressed()
    snod_name = np.ma.array(snod,mask=~mask).compressed()

    label=name.split('/')[0]
    
    #print(dt_name)
    #print(snod_name)
    #print(it_name)
    #exit()
    
    #the measurements/dates are not sorted
    #import to pandas, sort and make means and SD per measurement date
    dt_sorted,idx = np.unique(dt_name,return_inverse=True)
    #print(dt_sorted)
    #print(idx)
    
    snod_mean = np.zeros_like(dt_sorted)
    snod_std = np.zeros_like(dt_sorted)
    it_mean = np.zeros_like(dt_sorted)
    it_std = np.zeros_like(dt_sorted)
    for ii in range(0,len(dt_sorted)):
        mask_id = dt_name==dt_sorted[ii]
        #print(mask_id)
        #exit()
        
        ss=np.ma.array(snod_name,mask=~mask_id).compressed()
        snod_mean[ii] = np.mean(ss)
        snod_std[ii] = np.std(ss)
        
        tt=np.ma.array(it_name,mask=~mask_id).compressed()
        tt=np.ma.masked_invalid(tt)
        
        #print(dt_sorted[ii])
        #print(tt)
        it_mean[ii] = np.mean(tt)
        it_std[ii] = np.std(tt)

    ax.errorbar(dt_sorted,snod_mean,snod_std,marker='.', c=c[nn],ls='None',label=label)
    ax.errorbar(dt_sorted,it_mean,it_std,marker='.', c=c[nn],ls='None')
    
    #ax.plot(dt_name,snod_name,'x', c=c[nn])
    #ax.plot(dt_name,it_name,'x', c=c[nn])
    
    #write this into a file
    tt = [dt_sorted,snod_mean,snod_std,it_mean,it_std,it_mean,snod_mean,snod_std,snod_mean,snod_std]
    table = list(zip(*tt))

    file_ts = inpath_obs+'ts_'+label.split(' ')[0]+'.csv'

    print(file_ts)
    with open(file_ts, 'wb') as f:
        #header
        f.write(b'Date/Time, snow depth mean, snow depth SD, ice thickness mean, ice thickness SD, ice thickness mode, snow depth on level ice (mode+-10cm), snow depth on level ice STD, snow depth in deformed ice, snow depth on deformed ice STD\n')
        np.savetxt(f, table, fmt="%s", delimiter=",")




ax.set_ylabel('Ice thickness/Snow depth (m)',fontsize=20) # Y axis data label

ax.set_xlim(datetime(2019,9,1),datetime(2020,7,29))
#ax.set_ylim(-2.5,.5)

ax.tick_params(axis="x", labelsize=14)
ax.tick_params(axis="y", labelsize=14)

# Shrink current axis's height by 10% on the bottom
box = ax.get_position()
ax.set_position([box.x0, box.y0 + box.height * 0.1,
                 box.width, box.height * 0.9])

# Put a legend below current axis
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
          fancybox=True, shadow=False, ncol=4, fontsize=16)
#ax.legend(fontsize=18,loc='lower left',ncol=2)

fig1.autofmt_xdate()

#fig1.savefig(outpath+'sm_season_MOSAiC',bbox_inches='tight')
plt.show()


