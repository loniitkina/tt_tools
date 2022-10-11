import numpy as np
from glob import glob
from tt_func import getColumn, get_ice_mode, running_stats
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

inpath_grid = '../data/grids_AGU/'
inpath_table = '../data/MCS/MP/'
outpath = '../plots_meltponds/'
outname = 'PDF_recon_Jan.png'

#get all January GEM-transect PDFs!!!!
srbins = np.arange(0,.8,.02)
irbins = np.arange(0,9,.2)

#PDFs for the meltpond paper
fig1 = plt.figure(figsize=(15,5))
px = fig1.add_subplot(131)
px.set_xlabel('Snow depth (m)', fontsize=20)
px.set_ylabel('Probability', fontsize=20)
px.tick_params(axis="x", labelsize=14)
px.tick_params(axis="y", labelsize=14)
px.set_xlim(0,.9)
px.set_ylim(0,.13)

rx = fig1.add_subplot(132)
rx.set_xlabel('Ice thickness (m)', fontsize=20)
#rx.set_ylabel('Probability', fontsize=20)
rx.tick_params(axis="x", labelsize=14)
rx.tick_params(axis="y", labelsize=14)
rx.set_xlim(0,9)
rx.set_ylim(0,.23)

sx = fig1.add_subplot(133)
sx.set_xlabel('Total thickness (m)', fontsize=20)
#rx.set_ylabel('Probability', fontsize=20)
sx.tick_params(axis="x", labelsize=14)
sx.tick_params(axis="y", labelsize=14)
sx.set_xlim(0,9)
sx.set_ylim(0,.23)

#Nloop
step = 1
stp = str(step)
method_gem2 = 'nearest'
ch_name = '_18kHz'
loc = 'Nloop'
dates =['20191024','20191031','20191107','20191114','20191121','20191128','20191205',  '20191219','20191226','20200102','20200109','20200116','20200130','20200206','20200220','20200227', '20200305','20200320','20200326','20200403','20200416','20200424','20200430','20200507']

selection_meltpond=['20191107','20200130']

dt = [ datetime.strptime(x, '%Y%m%d') for x in dates ]
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
datel = [ datetime.strftime(x, '%b %d %Y') for x in dt ]
print(datel)

colors = plt.cm.rainbow(np.linspace(0, 1, len(dates)))

for dd in range(0,len(dates)):
    date = dates[dd]
    dt = datetime.strptime(date, '%Y%m%d')
    #dt_list.append(dt)
    print(date)
    
    inf = inpath_grid+loc+'_'+stp+'m_'+method_gem2+ch_name+'_track2.npz'
    data = np.load(inf)

    transect_snow = data['snow']
    transect_ice = data['ice']
    
    mxx = transect_snow[:,0]
    myy = transect_snow[:,1]
    si = transect_snow[:,dd+2]
    it = transect_ice[:,dd+2]
        
    #clean up the nans
    it = np.ma.masked_invalid(it)
    si = np.ma.array(si,mask=it.mask)
    
    mxx = np.ma.array(mxx,mask=it.mask); mxx = mxx.compressed()
    myy = np.ma.array(myy,mask=it.mask); myy = myy.compressed()

    si = si.compressed()
    it = it.compressed()
                    
    #how many snow depth measurements points should be used
    #decide this based on the MP spacing, so that it is the same total distance for all legs/sampling personel
    nit=50
    
    #running mean and variance
    itm,itv = running_stats(it,nit)
    std = np.sqrt(itv)
    
    sim,siv = running_stats(si,nit)    
    
    #first and last nit/2 values are zeros!!!
    std_whole = std.copy()
    mask = (sim==0) | np.isnan(sim) | np.isnan(std)
        
    #truncated original snow depths
    #truncated original ice thickness
    sitrunc = np.ma.array(si,mask=mask).compressed()
    ittrunc = np.ma.array(it,mask=mask).compressed()
        
    #PDF plots for meltpond paper
    if date in selection_meltpond:
        
        weights = np.ones_like(sitrunc) / (len(sitrunc))
        n, bins, patches = px.hist(sitrunc, srbins, histtype='stepfilled', color=colors[dd+5], linewidth=4, alpha=.5, weights=weights, label=datel[dd])

        weights = np.ones_like(ittrunc) / (len(ittrunc))
        n, bins, patches = rx.hist(ittrunc, irbins, histtype='stepfilled', color=colors[dd], linewidth=4, alpha=.5, weights=weights, label=datel[dd])

#recon
fname = inpath_table+'recon/magna+gem220200107_recon.csv'
it = getColumn(fname,8)
it = np.array(it,dtype=np.float)
    
weights = np.ones_like(it) / (len(it))
n, bins, patches = sx.hist(it, irbins, histtype='stepfilled', color='purple', linewidth=4, alpha=.5, weights=weights, label='Jan 07 2020')




print(outname)
px.legend(fontsize=17)
rx.legend(fontsize=17)
sx.legend(fontsize=17)

fig1.savefig(outpath+outname,bbox_inches='tight')


