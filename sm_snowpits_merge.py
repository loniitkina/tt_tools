import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from datetime import datetime
from glob import glob
from tt_func import getColumn, polymodel
import pandas as pd
import matplotlib.dates as mdates
from matplotlib.dates import MonthLocator, DateFormatter
import locale

#only print error to standard oputput (ignore warnings)
from matplotlib.axes._axes import _log as matplotlib_axes_logger
matplotlib_axes_logger.setLevel('ERROR')


outpath='../plots_sm/'
inpath_table = '../data/MCS/MP/'

#selected snow density values from SWE probe, density cutter and SMP
selection=['snow1','snow2','snow3','runway1','ds','L','DR','FR','RS3','Nloop']

##snow1 only (the most frequent and longest sampled site)
#selection=['snow1']

##ridges only
#selection=['DR','FR']

melt=datetime(2020,6,1)

colors = plt.cm.jet(np.linspace(0, 1, len(selection)))

#start a figure
fig1 = plt.figure(figsize=(15,8))
ax = fig1.add_subplot(111)

swe_list=[]
bulk_list=[]
date_list=[]

all_xd=[]
all_rho=[]

for j in range(0,len(selection)):
    snowpit_group=selection[j]
    print(snowpit_group,'****************************************************************************************')
    
    ##SMP and SWE cylinder bulk density
    fnames = sorted(glob('../data/snowpits_wagner/swe_smpdensity_leg1_leg3_archive/metdata_and_plot_qc/swe_smp_k2020_'+snowpit_group+'*.csv')+glob('../data/snowpits_amy/metadata_SWE_'+snowpit_group+'*.csv'))
    ##just SMP
    #fnames = sorted(glob('../data/snowpits_wagner/swe_smpdensity_leg1_leg3_archive/metdata_and_plot_qc/swe_smp_k2020_'+snowpit_group+'*.csv'))
    #just SWE cylinder
    #fnames = sorted(glob('../data/snowpits_amy/metadata_SWE_'+snowpit_group+'*.csv'))
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
        
        #individual SWE measurements
        ax.scatter(date,rho_s,marker='x',c='.5')

        #SMP has typically 5 measurements for each snow pit - and up to 25 in transects
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
                
        snod_m = np.ma.masked_invalid(means.depth.values)
        
        dates_m = np.ma.array(means.index.values,mask=snod_m.mask).compressed()
        swe_m = np.ma.array(means.swe.values,mask=snod_m.mask).compressed()
        rho_s_m = np.ma.array(means.density.values,mask=snod_m.mask).compressed()
        lon_m = np.ma.array(means.lon.values,mask=snod_m.mask).compressed()
        lat_m = np.ma.array(means.lat.values,mask=snod_m.mask).compressed()
        x_m = np.ma.array(means.x.values,mask=snod_m.mask).compressed()
        y_m = np.ma.array(means.y.values,mask=snod_m.mask).compressed()
        snod_m = snod_m.compressed()
        
        #plotting
        if i==0:
            if snowpit_group=='snow1':
                label='Snow 1'
            elif snowpit_group=='snow2':
                label='Snow 2'
            elif snowpit_group=='snow3':
                label='Snow 3'    
            elif snowpit_group=='FR':
                label='Fort Ridge' 
            elif snowpit_group=='DR':
                label='Davids Ridge'    
            elif snowpit_group=='RS3':
                label='RS Site 3'    
            elif snowpit_group=='L':
                label='L-Sites'
            elif snowpit_group=='ds':
                label='Dark Site'
            elif snowpit_group=='runway1':
                label='Runway'    
            else:
                label=snowpit_group
            ax.scatter(dates_m,rho_s_m,marker='s',c=colors[j],label=label)
            
        else:
            ax.scatter(dates_m,rho_s_m,marker='s',c=colors[j])
            
        
        #plot circles to show snow depth
        ax.scatter(dates_m,rho_s_m,marker='o',s=snod_m*700, facecolors='none', edgecolors='k')

        #convert to datetime
        dates_s_m = dates_m.astype('M8[D]').astype('O')
        
        #store for the curve
        bulk_list.extend(rho_s_m)
        date_list.extend(dates_s_m)
        
        #get density cutter values (if they exist)
        #this will give some cloud of all values (visualization on the plot)
        fcs = sorted(glob('../data/snowpits_amy/metadata_DensityCutter_'+snowpit+'*.csv'))
        if len(fcs)>0:
            fc=fcs[0]
            print(fc)
            
            #Date/time,doid,z top [m], z bottom [m],snow density [kg/m3],LAT,LON,x,y
            dtc = getColumn(fc,0)
            dtc = [ datetime.strptime(dtc[x], "%Y-%m-%d %H:%M:%S") for x in range(len(dtc)) ]
                        
            rho = getColumn(fc,4)
            rho = np.array(rho,dtype=np.float)

            ax.scatter(dtc,rho,marker='.',c='.75')
                        
            #estimate SWE from density cutter too
            h_s = getColumn(fc,2)
            h_s = np.array(h_s,dtype=np.float)
            
            h_e = getColumn(fc,3)
            h_e = np.array(h_e,dtype=np.float)

            #make daily groups
            snow = {'h_s': h_s,
                    'h_e': h_e,
                    'density': rho}

            df = pd.DataFrame(data=snow,index=dtc)
            days = df.groupby(pd.Grouper(freq='1D'))
            
            for dd in days:
                if len(dd[1]['h_s']) > 0:
                    #print(dd)
                    
                    h_start = dd[1]['h_s'].values
                    h_end = dd[1]['h_e'].values
                    rho = dd[1]['density'].values
                    
                    dt_pit = dd[1]['density'].index[0]
                
                    #sometimes there is only top layer sampled - throw those snow pits away
                    #here we set this value high - we use as many data points as possible
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
                        rho=rho.filled(fill_value=mean_rho)
                        
                        ##before December there was no such wind slab, so we can lower this limit to 400
                        #if dtc < datetime(2019,12,1):
                            ##print('early winter')
                            #rho = np.ma.array(rho,mask=rho>400)
                            #mean_rho = np.mean(rho)
                            #rho=rho.filled(fill_value=mean_rho)
                        
                        #calculate SWE
                        swe = np.sum( rho/1000 *layer  ) + rest
                        
                        #calculate bulk density
                        bulk = (swe/snod)*1000
                        
                        xd = [ dtc for x in range(len(rho)) ]
                        #ax.scatter(xd,rho,marker='.',c=colors[i])
                        
                        all_xd.extend(xd)
                        all_rho.extend(rho)
                        
                        #plot bulk density
                        ax.scatter(dt_pit,bulk,marker='d',c=colors[j])

                        #plot circles to show snow depth
                        ax.scatter(dt_pit,bulk,marker='o',s=snod*700, facecolors='none', edgecolors='k')
                        
                        ##save SWE and bulk density for curve fitting
                        swe_list.append(swe)
                        bulk_list.append(bulk)
                        date_list.append(dt_pit)

#fit the curve
#dont use any values from the melt period
mask=np.array(date_list,dtype=np.datetime64)>np.datetime64(melt)
date_list = np.ma.array(date_list).compressed()
bulk_list = np.ma.array(bulk_list).compressed()

x = mdates.date2num(date_list) #convert time tuples to numbers
y = bulk_list
model = np.polyfit(x, y, 1) #decide here the curve-order
predict = np.poly1d(model)

xmodel = np.arange(min(x),max(x),1) #convert numbers to dates for plotting
dd = mdates.num2date(xmodel)
ymodel = predict(xmodel)

ax.plot(dd, ymodel, color='darkred',ls=':',alpha=.9,lw=3)

#add 20% above and bellow lines
ax.plot(dd, ymodel+(.2*ymodel), color='.8',ls='--',alpha=.9,lw=3)
ax.plot(dd, ymodel-(.2*ymodel), color='.8',ls='--',alpha=.9,lw=3)


legend1=ax.legend(ncol=5,fontsize=14)
ax.set_ylim(0,450)
ax.set_xlim(datetime(2019,10,20),melt)
ax.set_ylabel('Snow density (kg/m$^3$)',fontsize=20)
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
legend2 = ax.legend(elements, [f" {p:.1f} m" for p in legend_values], loc='lower right', title="Snow depth")
ax.add_artist(legend2)

#keep the first legend
plt.gca().add_artist(legend1)

plt.show()
fig1.savefig(outpath+'bulk_density_curve1.png',bbox_inches='tight')
exit()


#open the transect data
loc='Sloop'
#loc='Nloop'
#loc='runway'
for i in ['level','rubble']:
    fname = inpath_table+'SnowModel_'+loc+'_'+i+'.csv'
    fname = inpath_table+'SnowModel_'+loc+'_'+i+'_melt.csv'
    print(fname)

    sloop_dates = getColumn(fname,0)
    sloop_si = getColumn(fname,1)
    sloop_si = np.array(sloop_si,dtype=np.float)
    sloop_sid = getColumn(fname,2)
    sloop_it = getColumn(fname,3)
    sloop_itd = getColumn(fname,4)
    sloop_itm = getColumn(fname,5)

    #extract the bulk density for the dates when we have the transects:
    sloop_dates = [ datetime.strptime(x, "%Y%m%d") for x in sloop_dates ]
    print(sloop_dates)
    x = mdates.date2num(sloop_dates)
    sloop_rho = predict(x)
    print(sloop_rho)

    #set 550 density (saturated/melting snow) for all summer data
    for x in range(0,len(sloop_dates)):
        if sloop_dates[x] > datetime(2020,6,1):
            sloop_rho[x] = 550
            

    #calculate SWE for those dates
    sloop_swe = sloop_rho/1000 *sloop_si
    print(sloop_swe)

    #prepare output for SnowModel
    year = [ datetime.strftime(x, "%Y") for x in sloop_dates ]
    month = [ datetime.strftime(x, "%m") for x in sloop_dates ]
    day = [ datetime.strftime(x, "%d") for x in sloop_dates ]

    #save the data in files
    file_name = fname.split('.csv')[0]+'_swe.csv'
    print(file_name)

    tt = [year,month,day,sloop_si,sloop_sid,sloop_it,sloop_itd,sloop_itm,sloop_rho,sloop_swe]
    table = list(zip(*tt))

    with open(file_name, 'wb') as f:
        #header
        f.write(b'year,month,day,snow depth (m),snow depth std (m),ice thickness (m),ice thickness std (m), ice thickness mode (m), snow density (kg/m3), SWE (m)\n')
        np.savetxt(f, table, fmt="%s", delimiter=",")
        
        
