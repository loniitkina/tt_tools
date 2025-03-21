import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from datetime import datetime, date
from glob import glob
from tt_func import getColumn, polymodel
import pandas as pd
import matplotlib.dates as mdates
from matplotlib.dates import MonthLocator, DateFormatter
import locale

#The transect input for this script is produced by two separate scripts: 
#tt_pdf_plot.py: This gives mean and mode values for combined transect line and also for the level and deformed ice
#in Itkin et al, 2023 the level ice values for Sloop are calculated form the gridded colocated data for the Sloop.
#The summer data is not collocted (no FloeNavi and lots of rotations), so we used a more simple level ice definition:
#sea ice thickness mode +-10cm

#give some time limit the snow pit density data - during summer site slection is not representative, all pits are in the ridges
timelimit=datetime(2020,6,1,0,0,0)

period=False #weather and deformation periods - this is only used in post-procesing of results

#pick which sampling method
method='all'
#method='swe'   #just the SWE cylinder for the bulk density

#by turning this on this script produces reduced snow cover (by one standard deviation)
treat=['normal','level','level_low']

outpath='../plots_sm/'
inpath_table = '../data/MCS/MP/SnowModel_calval/'   #these data is created by tt_pdf_plot.py

#groups of repeated snowpits by SWE probe, density cutter and SMP
selection=['Nloop','snow1','snow2','snow3','runway1','DS-coring-FYI','DS-coring-SYI','L','FR','DR','RS','radiation','optics','SYI','stakes1']
#selection=['Nloop','snow1','snow2','snow3','runway1','DS-coring-FYI','DS-coring-SYI','L','FR','DR','RS','radiation']
#selection=['Nloop','snow1','snow2','snow3','runway1','DS-coring-FYI','DS-coring-SYI','L','FR','DR','RS']

#SMP values
#A5* was merged into A5 file
#RS-transect-north measurements that were flagged in meta-file were removed

labels = ['Nloop','Snow 1','Snow 2','Snow 3','Runway','Dark Site FYI','Dark Site SYI','L-sites','Fort Ridge','Davids Ridge','RS sites','Radiation','Optics','Allies Ridge','Stakes 1']

#labels = ['Nloop','Runway','Stakes 1','MetCity']

markers = ['o','o','o','o','o','o','o','o','v','v','v','v','v','v','v','v']
colors = ['salmon','purple','fuchsia','cornflowerblue','gold','teal','limegreen','deeppink','darkred','darkorange','r','b','y','g','c','purple']

#start a figure
fig1 = plt.figure(figsize=(15,11))
ax = fig1.add_subplot(111)

bulk_list=[]
date_list=[]

bulk_list_smp=[]
date_list_smp=[]

bulk_list_swe=[]
date_list_swe=[]

bulk_list_cutter=[]
date_list_cutter=[]

all_xd=[]
all_rho=[]

smp_count=0
cutter_count=0
swe_count=0

for j in range(0,len(selection)):
    snowpit_group=selection[j]
    snowpit_group_label=labels[j]
    print(snowpit_group,'**********************************************************')

    #SMP and SWE cylinder bulk density
    fnames = sorted(glob('../data/snowpits_wagner/swe_smpdensity_leg1_leg3_archive/metdata_and_plot_qc/swe_smp_k2020_'+snowpit_group+'*.csv')+glob('../data/snowpits_amy/metadata_SWE_'+snowpit_group+'*.csv'))
    
    #fnames = sorted(glob('../data/snowpits_amy/metadata_SWE_'+snowpit_group+'*.csv'))

    group=[]
    group_d=[]
    dates_g=[]

    for i in range(0,len(fnames)):
        fname = fnames[i]
        snowpit = fname.split('_')[-1].split('.csv')[0]

        print(snowpit)
        #Date/time,doid,z [m],SWE [mm],LAT,LON,x,y,bulk snow density [kg/m3]
        dt = getColumn(fname,0)
        date = [ datetime.strptime(dt[x], "%Y-%m-%d %H:%M:%S") for x in range(len(dt)) ]

        snod = getColumn(fname,2)
        snod = np.array(snod,dtype=np.float)
        swe = getColumn(fname,3)
        swe = np.array(swe,dtype=np.float)
        lat = getColumn(fname,4)
        lat = np.array(lat,dtype=np.float)
        lon = getColumn(fname,5)
        lon = np.array(lon,dtype=np.float)
        x = getColumn(fname,6)
        x = np.array(x,dtype=np.float)
        y = getColumn(fname,7)
        y = np.array(y,dtype=np.float)
        rho_s = getColumn(fname,8)
        rho_s = np.array(rho_s,dtype=np.float)

        #make daily means
        snow = {'depth': snod,
                'swe': swe,
                'density': rho_s,
                'lon': lon,
                'lat': lat,
                'x': x,
                'y':y}

        df = pd.DataFrame(data=snow,index=date)
        means = df.groupby(pd.Grouper(freq='1D')).mean()
        
        #keep values
        #print(means.index.values)
        #print(means.depth.values)
        
        snod_m = np.ma.masked_invalid(means.depth.values)
        
        dates_m = np.ma.array(means.index.values,mask=snod_m.mask).compressed()
        swe_m = np.ma.array(means.swe.values,mask=snod_m.mask).compressed()
        rho_s_m = np.ma.array(means.density.values,mask=snod_m.mask).compressed()
        lon_m = np.ma.array(means.lon.values,mask=snod_m.mask).compressed()
        lat_m = np.ma.array(means.lat.values,mask=snod_m.mask).compressed()
        x_m = np.ma.array(means.x.values,mask=snod_m.mask).compressed()
        y_m = np.ma.array(means.y.values,mask=snod_m.mask).compressed()
        snod_m = snod_m.compressed()
        
        #convert to datetime
        dates_m = dates_m.astype('M8[D]').astype('O')
        
        group.extend(rho_s_m)
        dates_g.extend(dates_m)
        #print(dates_m)
        group_d.extend(snod_m*700)
        
        if fname.split('/')[2] == 'snowpits_wagner':
            smp_count=smp_count+len(rho_s_m)
            bulk_list_smp.extend(rho_s_m)
            date_list_smp.extend(dates_m)
        else:
            swe_count=swe_count+len(rho_s_m)
            bulk_list_swe.extend(rho_s_m)
            date_list_swe.extend(dates_m)
    
        #get density cutter values
        fcs = sorted(glob('../data/snowpits_wagner/swe_smpdensity_leg1_leg3_archive/cutter/cutter_*'+snowpit+'*.csv'))
        #print(fcs)
    
        for fc in fcs:
            #print(fc)
            dtc = fc.split('_')[6]
            dtc = datetime.strptime(dtc, "%Y%m%d")

            rho = getColumn(fc,6)
            rho = np.array(rho,dtype=np.float)
            
            h_start = getColumn(fc,4)
            h_start = np.array(h_start,dtype=np.float) /100
            
            h_end = getColumn(fc,5)
            h_end = np.array(h_end,dtype=np.float) /100
            
            #sometimes there is only top layer sampled - throw those snow pits away
            #here we set this value high - we use as many data points as possible (they fit the curve well)
            if h_end[-1] < 0.25:    
                
                #check how much we are missing and assign SWE to the lowest part (same as layer above)
                if h_end[-1] > 0:
                    rest= rho[-1]/1000 *h_end[-1]
                else:
                    rest=0

                #snow depth is the top of the first density measurements
                snod = h_start[0]
                
                #check that tops of the consecutive density measuremnts are always 3cm appart
                #zero thickness will remove all double measurements
                layer = h_start[0:]-np.append(h_start[1:],h_end[-1])
                #print(layer)
                                
                #remove unrealistic snow densities > 550 (melting layer, 450 is the densest wind slab)
                #all our snow pits are from winter, so 450 is set as upper limit
                rho = np.ma.array(rho,mask=rho>450)
                                
                #replace those masked values by mean for the snow pit
                mean_rho = np.mean(rho)
                rho=rho.filled(fill_value=450)
                
                #before December there was no such wind slab, so we can lower this limit to 400
                if dtc < datetime(2019,12,1):
                    #print('early winter')
                    rho = np.ma.array(rho,mask=rho>400)
                    mean_rho = np.mean(rho)
                    rho=rho.filled(fill_value=400)
                    
                #print(rho)
                
                #calculate SWE
                swe = np.sum( rho/1000 *layer  ) + rest
                
                #calculate bulk density
                bulk = (swe/snod)*1000
                print(bulk)
                
                xd = [ dtc for x in range(len(rho)) ]
                #ax.scatter(xd,rho,marker='.',c=colors[i])
                
                all_xd.extend(xd)
                all_rho.extend(rho)
                
                #save bulk density for curve fitting
                group.append(bulk)
                dates_g.append(dtc)
                group_d.append(snod*700)
                
                bulk_list_cutter.append(bulk)
                date_list_cutter.append(dtc)
                
                cutter_count=cutter_count+1

            else:
                print('lower part of pit missing: ', h_end[-1])
            
    #limit to the winter
    print(timelimit)
    dates_g = np.array(dates_g,dtype=np.datetime64)
    #print(dates_gg)
    try:
        mask = dates_g > timelimit
        dates_g = np.ma.array(dates_g,mask=mask).compressed()
        group = np.ma.array(group,mask=mask).compressed()
        group_d = np.ma.array(group_d,mask=mask).compressed()
    except: #some snow pits have only few measurements and cause problems - they are just winter anyway
        print('problems in: ',snowpit_group_label)
        
    
   
    
    ax.scatter(dates_g,group,marker=markers[j],c=colors[j],label=snowpit_group_label)
    
    #plot circles to show snow depth
    ax.scatter(dates_g,group,marker='o',s=group_d, facecolors='none', edgecolors='k')
    
    #store for the curve
    bulk_list.extend(group)
    date_list.extend(dates_g.tolist())
            
            
#all cutter values inside the pits
ax.scatter(all_xd,all_rho,marker='.',c='.75')
ax.set_ylim(min(all_rho),max(all_rho))
#ax.set_ylim(50,500)
       
#fit the curve

x = mdates.date2num(date_list) #convert time tuples to numbers, Number of days since the epoch. See get_epoch for the epoch, which can be changed by rcParams["date.epoch"] (default: '1970-01-01T00:00:00') 
y = bulk_list

#This is the first snow pit observation, subtract to get the coefficient right
date_subtract = mdates.date2num(datetime(2019,10,25))
x = x - date_subtract

order_color=['darkred','b','r','y','g']
for i in range(1,2):
    print('order: ',i)
    model_all = np.polyfit(x, y, i) #decide here the curve-order
    predict = np.poly1d(model_all)

    xmodel = np.arange(min(x),max(x),1) #convert numbers to dates for plotting
    dd_all = mdates.num2date(xmodel + date_subtract)
    ymodel_all = predict(xmodel)

    ax.plot(dd_all, ymodel_all, color=order_color[i-1],ls='--',alpha=.9,lw=3,label='all',zorder=0)#,label=i)
    
    #print(dd)
    #print(ymodel)
    #plt.grid()
    
    print('counts')
    print('smp: ',smp_count)
    print('SWE: ',swe_count)
    print('cutter: ',cutter_count)
    
    #get the model formula written out
    print('coefficients: ', model_all)
    ss = np.round(model_all[0],2)
    ii = model_all[1]
    ax.text(datetime(2019,11,20),430,r"$\rho_s = %r x + %i \frac{kg}{m^3}$" %(ss,ii), fontsize=18)
    ax.text(datetime(2019,11,20),410,r"$N = %i$" %(smp_count+swe_count+cutter_count), fontsize=18)

#individual methods
#cutter
x = mdates.date2num(date_list_cutter)
y = bulk_list_cutter
model = np.polyfit(x, y, 1)
predict_cutter = np.poly1d(model)
xmodel = np.arange(min(x),max(x),1)
dd = mdates.num2date(xmodel)
ymodel = predict_cutter(xmodel)
ax.plot(dd, ymodel, color='y',ls=':',alpha=.9,lw=3,label='cutter',zorder=0)
ax.scatter(date_list_cutter,bulk_list_cutter,marker='.',c='w',s=10)

#SMP
x = mdates.date2num(date_list_smp)
y = bulk_list_smp
model = np.polyfit(x, y, 1)
predict_smp = np.poly1d(model)
xmodel = np.arange(min(x),max(x),1)
dd = mdates.num2date(xmodel)
ymodel = predict_smp(xmodel)
ax.plot(dd, ymodel, color='g',ls=':',alpha=.9,lw=3,label='SMP',zorder=0)

#SWE
x = mdates.date2num(date_list_swe)
y = bulk_list_swe
model = np.polyfit(x, y, 1)
predict_swe = np.poly1d(model)
xmodel = np.arange(min(x),max(x),1)
dd = mdates.num2date(xmodel)
ymodel = predict_swe(xmodel)
ax.plot(dd, ymodel, color='b',ls=':',alpha=.9,lw=3,label='cylinder',zorder=0)
ax.scatter(date_list_swe,bulk_list_swe,marker='x',c='k',s=20)

#add 20% above and bellow lines
ax.plot(dd_all, ymodel_all+(.2*ymodel_all), color='.75',ls='--',alpha=1,lw=3,zorder=0)
ax.plot(dd_all, ymodel_all-(.2*ymodel_all), color='.75',ls='--',alpha=1,lw=3,zorder=0)

legend1=ax.legend(ncol=5,fontsize=14, loc='lower right')
#ax.set_ylim(0,450)
ax.set_xlim(datetime(2019,10,20),datetime(2020,5,15))
ax.set_ylabel(r'Snow density ($\frac{kg}{m^3}$)',fontsize=20)
ax.tick_params(axis="x", labelsize=14)
ax.tick_params(axis="y", labelsize=14)

#nicer dates
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
ax.xaxis.set_minor_locator(MonthLocator())
ax.xaxis.set_major_formatter(DateFormatter('%b %Y'))

#snow depth legend
legend_values = np.array([.1,.2,.5])
legend_sizes = legend_values*700

# IMPORTANT: for some reason the square root needs to be applied to sizes in the legend
legend_sizes_sqrt = np.sqrt(legend_sizes)

elements = [plt.Line2D([0], [0], color='none', marker="o", markerfacecolor=None, markeredgecolor='k', markersize=s) for s in legend_sizes_sqrt]
legend2 = ax.legend(elements, [f" {p:.1f} m" for p in legend_values], loc='upper left', title="Snow depth",fontsize=14,title_fontsize='x-large')
ax.add_artist(legend2)

#keep the first legend
plt.gca().add_artist(legend1)

#plt.show()
fig1.savefig(outpath+'bulk_density_curve4.png')
#plt.show()
exit()

if method=='swe':
    predict=predict_swe

#open the transect data
loc='Sloop'
loc='Nloop'
#loc='runway'
#loc='runwayup'
#loc='runwaydown'
for i in treat:
    #use means as they are plotted in Itkin et al, 2023
    #melt data is added from 'special' on 17 June and 'transect' of leg 4
    #files created in tt_pdf_plot.py
    fname = inpath_table+'ts_'+loc+'_1m_gridded_melt.csv'
    fname = inpath_table+'ts_'+loc+'_1m_gridded_melt_new.csv'
    if period:
        fname = inpath_table+'ts_'+loc+'_1m_gridded_period.csv'
    print(fname)

    #read snow depth mean, level ice or get reduced level ice snow depth, depending on the 'treat'
    if i=='normal':
        sn=1;snd=2
    elif i=='level':
        sn=6;snd=7
    elif i=='level_low':
        sn=6;snd=7

    loc_dates = getColumn(fname,0)
    loc_si = getColumn(fname,sn)
    loc_si = np.array(loc_si,dtype=np.float)
    loc_sid = getColumn(fname,snd)
    loc_it = getColumn(fname,3)
    loc_itd = getColumn(fname,4)
    loc_itm = getColumn(fname,5)

    #extract the bulk density for the dates when we have the transects:
    loc_dates = [ datetime.strptime(x, "%Y%m%d") for x in loc_dates ]
    #print(loc_dates)
    x = mdates.date2num(loc_dates)
    loc_rho = predict(x)
    print(loc_rho)

    #set 550 density (saturated/melting snow) for all summer data
    for x in range(0,len(loc_dates)):
        if loc_dates[x] > datetime(2020,6,1):
            loc_rho[x] = 550
    
    if i=='level_low':
        loc_sid = np.array(loc_sid,dtype=np.float)
        #prepare a file with snowdepth and SWE reduced by 1SD
        loc_si = loc_si - loc_sid
        
        #check that there are no negative values
        loc_si = np.where(loc_si<0,0,loc_si)

    #calculate SWE for those dates
    loc_swe = loc_rho/1000 *loc_si
    #print(loc_swe)
    
    #prepare output for SnowModel
    year = [ datetime.strftime(x, "%Y") for x in loc_dates ]
    month = [ datetime.strftime(x, "%m") for x in loc_dates ]
    day = [ datetime.strftime(x, "%d") for x in loc_dates ]

    #save the data in files
    file_name = fname.split('.csv')[0]+'_swe_'+i+'.csv'
    print(file_name)

    tt = [year,month,day,loc_si,loc_sid,loc_it,loc_itd,loc_itm,loc_rho,loc_swe]
    table = list(zip(*tt))

    with open(file_name, 'wb') as f:
        #header
        f.write(b'year,month,day,snow depth (m),snow depth std (m),ice thickness (m),ice thickness std (m), ice thickness mode (m), snow density (kg/m3), SWE (m)\n')
        np.savetxt(f, table, fmt="%s", delimiter=",")
        
    #also calculate the snow thermal conductivity, following macfarnale et al, 2023
    #rks = (2.62e-6 * sden ** 2) + (1.54e-33 * sden) + 3.04e-2
    rks = (2.62e-6 * loc_rho ** 2) + (1.54e-33 * loc_rho) + 3.04e-2
    
    print('snow thermal conductivity')
    print(rks)
    


