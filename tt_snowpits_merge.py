import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from datetime import datetime
from glob import glob
from tt_func import getColumn, polymodel
import pandas as pd
import matplotlib.dates as mdates

outpath='../plots_gridded/'
inpath_table = '../data/MCS/MP/'

#snow pits
#A5* was merged into A5 file
#RS-transect-north measurements that were flagged in meta-file were removed
fnames = sorted(glob('../data/snowpits_wagner/swe_smpdensity_leg1_leg3_archive/metdata_and_plot_qc/swe_smp_k2020_*.csv'))
selection = ['snow1-A1','snow1-A3','snow1-A5','runway1','RS-transect-north']
selection = ['runway1','snow1-','snow1-A1-dune','snow1-A1','snow1-A3','snow1-A4-RS','snow1-A5*','snow1-A5','snow1-A9','snow1-lead','snow1-transect','snow2-A10','snow2-A11','snow2-A12-transect','snow2-A2','snow2-A8','snow2-lead','snow3-A6-side','snow3-A6']

##level ice close to trasects
#selection = ['runway1','snow1-','snow1-A1-dune','snow1-A1','snow1-A3','snow1-A4-RS','snow1-A5','snow1-A9','snow1-lead','snow1-transect','RS-transect-north']



##level (and close to ridges) and deformed ice: snow2 and snow3
##large horizontal variability, and seemingly preferential sampling in thin snow in spring
#selection = ['snow2-A10','snow2-A11','snow2-A12-transect','snow2-A2','snow2-A8','snow2-lead','snow3-A6-side','snow3-A6']

colors = plt.cm.rainbow(np.linspace(0, 1, len(fnames)))

#start a figure
fig1 = plt.figure(figsize=(15,8))
ax = fig1.add_subplot(111)

swe_list=[]
bulk_list=[]
date_list=[]

all_xd=[]
all_rho=[]

for i in range(0,len(fnames)):
    fname = fnames[i]
    snowpit = fname.split('_')[-1].split('.csv')[0]
    
    if snowpit in selection:
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
        
        #ax.scatter(date,rho_s)
        ax.scatter(dates_m,rho_s_m,marker='s',c=colors[i],label=snowpit)
        
        #plot circles to show snow depth
        ax.scatter(dates_m,rho_s_m,marker='o',s=snod_m*700, facecolors='none', edgecolors='k')

        #convert to datetime
        dates_s_m = dates_m.astype('M8[D]').astype('O')
        
        #store for the curve
        bulk_list.extend(rho_s_m)
        date_list.extend(dates_s_m)
        
        #get density cutter values
        fcs = sorted(glob('../data/snowpits_wagner/swe_smpdensity_leg1_leg3_archive/cutter/cutter_*'+snowpit+'*.csv'))
        #print(fcs)
        
        for fc in fcs:
            print(fc)
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
                rho=rho.filled(fill_value=mean_rho)
                
                #before December there was no such wind slab, so we can lower this limit to 400
                if dtc < datetime(2019,12,1):
                    #print('early winter')
                    rho = np.ma.array(rho,mask=rho>400)
                    mean_rho = np.mean(rho)
                    rho=rho.filled(fill_value=mean_rho)
                    
                #print(rho)
                
                #calculate SWE
                swe = np.sum( rho/1000 *layer  ) + rest
                
                #calculate bulk density
                bulk = (swe/snod)*1000
                
                xd = [ dtc for x in range(len(rho)) ]
                #ax.scatter(xd,rho,marker='.',c=colors[i])
                
                all_xd.extend(xd)
                all_rho.extend(rho)
                
                #plot bulk density
                ax.scatter(dtc,bulk,marker='s',c=colors[i])
                
                #plot circles to show snow depth
                ax.scatter(dtc,bulk,marker='o',s=snod*700, facecolors='none', edgecolors='k')
                
                ##save SWE and bulk density for curve fitting
                swe_list.append(swe)
                bulk_list.append(bulk)
                date_list.append(dtc)

            else:
                print('lower part of pit missing: ', h_end[-1]);continue
            
#all cutter values inside the pits
ax.scatter(all_xd,all_rho,marker='.',c='.75')
ax.set_ylim(min(all_rho),max(all_rho))
       
#fit the curve
x = mdates.date2num(date_list) #convert time tuples to numbers
y = bulk_list
model = np.polyfit(x, y, 1) #decide here the curve-order
predict = np.poly1d(model)

xmodel = np.arange(min(x),max(x),1) #convert numbers to dates for plotting
dd = mdates.num2date(xmodel)
ymodel = predict(xmodel)

ax.plot(dd, ymodel, color='darkred',ls=':',alpha=.9,lw=3)

#add 20% above and bellow lines
ax.plot(dd, ymodel+(.2*ymodel), color='.9',ls='--',alpha=.9,lw=3)
ax.plot(dd, ymodel-(.2*ymodel), color='.9',ls='--',alpha=.9,lw=3)

ax.legend()
#plt.show()
fig1.savefig(outpath+'bulk_density_curve.png')

#open the transect data
loc='Sloop'
#loc='Nloop'
#loc='runway'
for i in ['level','rubble']:
    fname = inpath_table+'SnowModel_'+loc+'_'+i+'.csv'
    #fname = inpath_table+'SnowModel_'+loc+'_'+i+'_melt.csv'
    
    #use means as they are plotted in Itkin et al, 2023
    #fname = inpath_table+'ts_Nloop_1m_gridded.csv'
    #fname = inpath_table+'ts_Nloop_1m_gridded_melt.csv' #add melt period data (copy from special on 17 June and transect of leg 4)
    #fname = inpath_table+'ts_Sloop_1m_gridded_melt.csv'
    #fname = inpath_table+'ts_runway_1m_gridded_melt.csv'
    fname = inpath_table+'ts_Sloop_1m_gridded.csv'
    
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
        
        
