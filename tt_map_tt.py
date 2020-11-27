import numpy as np
from glob import glob
from tt_func import getColumn
import matplotlib.pyplot as plt

#grid parameters
stp = 5        #grid spacing in meters 
maxdist = stp   #how far away to search in case of nan
#maxdist = 5

#location and dates
#loc = 'Nloop'
loc = 'Sloop'
fixed_date = '20200220'
#dates = ['20200220','20200102']
dates = ['20200220','20200130','20200109','20200102','20191226']

#events Sloop
fixed_date = '20191107'
dates = ['20191107','20191205','20200227','20200330']

#loc = 'snow1'
#fixed_date = '20191222'
#dates = ['20191222','20200112','20200126','20200207'] #'20200112' has no GEM-2 data
##dates = ['20191222','20200207']

##long transect
#loc = 'ANJA_36_special'
#fixed_date = '20200123'
#dates = ['20200123']



print(loc)
colors = plt.cm.rainbow(np.linspace(0, 1, len(dates)))

inpath = '../data/MCS/MP/'
outpath = '../plots_AGU/'
inpath_grid = '../data/grids_AGU/'
outname = 'profile_'+loc+str(stp)+'.png'

#choose one 'most perfct' MP track to compare to the others
fname = glob(inpath+'*/magnaprobe-transect-'+fixed_date+'*'+loc+'-track-icecs-xy_corr.csv')[0]
print(fname)
mxx = getColumn(fname,3, delimiter=',', magnaprobe=False)
mxx = np.array(mxx,dtype=np.float)

myy = getColumn(fname,4, delimiter=',', magnaprobe=False)
myy = np.array(myy,dtype=np.float)

#fix cooridinate shift
if fixed_date == '20200220':
    mxx = mxx-10

    if loc == 'Nloop':
        myy = myy-3

if fixed_date == '20191222':
    mxx = mxx+3
    myy = myy+3

#long transect (ice on 3 different groups of floes moving actively and independently)
if fixed_date == '20200123':
    print(len(mxx))
    mxx[:300] = mxx[:300]+15
    mxx[500:] = mxx[500:]-5


#get distances between fixed date MP points
dx = mxx[1:]-mxx[:-1]
dy = myy[1:]-myy[:-1]
md = np.sqrt(dx**2+dy**2)

#what is the surface elevation? ALS geotiff???
#hydrostatic equilibtium with mean snow density and sea ice density
rho_i = 882
rho_w = 1025
rho_s = 313

#plot
fig1 = plt.figure(figsize=(20,10))
ax = fig1.add_subplot(111)
ax.set_title(loc)
ax.set_xlabel('Length (m)')

for dd in range(0,len(dates)):
    date = dates[dd]
    print(date)
    
    #load all the gridded data
    of = inpath_grid+loc+'_'+date+'_'+str(stp)+'m.npz'
    #of = inpath_grid+loc+'_'+date+'_'+stp+'m_linear.npz')
    print(of)
    data = np.load(of)

    x_grid = data['x']
    y_grid = data['y']
    s_grid = data['snow']
    i_grid = data['ice']
    
    #quick check
    #ax.subplot(111)
    #ax.imshow(s_grid.T, extent=(-500,700,-900,700), origin='lower',vmin=0,vmax=1.2, cmap=cmaps[i])
    #ax.colorbar()
    #ax.title('Snow')
    #ax.gcf().set_size_inches(6, 6)
    #ax.show()
    #exit()

    #unroll the data back into the transect and draw them
    #find nearest grid point for each MP point of a sample MP transect (e.g. 20.2.2020)
    #order these grid points in a row

    si = []
    ii = []
    for i in range(0,len(mxx)):
        xi = mxx[i]
        yi = myy[i]
        #calculate all distances to grid points
        dg = np.sqrt((xi-x_grid)**2+(yi-y_grid)**2)
        #imin = np.min(dg)
        amin = np.argmin(dg)
        
        val_s = s_grid.flatten()[amin]
        val_i = i_grid.flatten()[amin]
        
        #if step < 5m, we need to take more distances to account, dont got further than maxdist away!
        if np.isnan(val_s):
            print('no value')
            dist = 0
            mask_dg = np.zeros_like(dg.flatten())
            while np.isnan(val_s) and dist < maxdist:
                mask_dg[amin]=1
                dg = np.ma.array(dg.flatten(),mask=mask_dg)
                amin = np.argmin(dg)
                dist = dg[amin]
                val_s = s_grid.flatten()[amin]
                val_i = i_grid.flatten()[amin]
            print(dist,val_s)
        
        si.append(val_s)
        ii.append(val_i)

    si = np.array(si)
    ii = np.array(ii)
    
    if loc=='Sloop' and date == '20191226':
        bad = np.zeros_like(ii)
        bad[700:] = 1
        ii = np.ma.array(ii,mask=bad)

    #what is the surface elevation? ALS geotiff???
    #hydrostatic equilibtium with mean snow density and sea ice density
    rho_i = 882
    rho_w = 1025
    rho_s = 313

    if date == fixed_date:
        #following Forsstrom et al, 2011, Annals of Glaciology
        fb = (ii - si * (rho_s/(rho_w-rho_i))) * (rho_w-rho_i)/rho_w
        x = range(0,len(fb))
        
        #cumulative distance allong the fixed date MP transect
        x = np.zeros_like(fb)
        x[1:] = np.cumsum(md)
        #print(x)
        #exit()

        #plot with equilibrium
        ax.plot(x,fb,label='ice surface',c='k',ls=':')
        
    #ax.plot(fb-ii,label='ice bottom'+date)
    #ax.plot(fb+si,label='snow surface'+date)
    ax.fill_between(x, fb, fb-ii,alpha=.3, color=colors[dd])
    ax.fill_between(x, fb, fb+si,alpha=.3, color=colors[dd],label=date)

ax.set_ylim(-6,2)
ax.set_xlim(0,x[-2])        #beacause last MP value/coordinate is typically same as first (at large distance)
ax.legend()
print(outname)
fig1.savefig(outpath+outname)



