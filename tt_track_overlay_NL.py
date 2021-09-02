import numpy as np
from glob import glob
from tt_func import getColumn
import matplotlib.pyplot as plt

#manually find the best overlay between the GEM-2 and MP tracks - different for each date
#take GEM-2 position as the better one and adjust MP to it

#also shift lateraly whole transects relativelly to the selected fixed date

#how to account for rotation???

#save file with shifted x,y coordinates

inpath = '../data/NansenLegacy/gem2/'

inpath_mp = '../data/NansenLegacy/magnaprobe/'

outpath = '../plots_NL/'

#limit location-wise
locs = ['P4']
locs = ['P5']
#locs = ['P6']
locs = ['P7a','P7b']

#plot
fig1 = plt.figure(figsize=(10,10))

#all the files
flist = glob(inpath+'*/*-track-icecs-xy.csv')
flist.sort()

dtot = 0
dtot_mp = 0
n_mp = 0
mp_spacing=[]

for i in range(0,len(flist)):
    if flist[i] !=flist[3]: continue
    fname = flist[i]
    print(fname)
    
    date = fname.split('/')[-1].split('-')[2]
    
    xx = getColumn(fname,3, delimiter=',', magnaprobe=False)
    xx = np.array(xx,dtype=np.float)
    
    yy = getColumn(fname,4, delimiter=',', magnaprobe=False)
    yy = np.array(yy,dtype=np.float)
    
    #GEM-2 files contain nans
    xx = np.ma.masked_invalid(xx)
    yy = np.ma.masked_invalid(yy)
        
    dx = xx[1:]-xx[:-1]
    dy = yy[1:]-yy[:-1]
    d = np.sum(np.sqrt(dx**2+dy**2))
    
    print('transect length:')
    print(d)
    print('GEM-2 measurement spacing:')
    spacing = np.mean(np.sqrt(dx**2+dy**2))
    print(spacing)

    dtot = dtot+d
    
    mp_list = glob(inpath_mp+'*/*'+date+'*-track-icecs-xy.csv')
    
    for sf in mp_list:
        print(sf)
        mxx = getColumn(sf,3, delimiter=',', magnaprobe=False)
        mxx = np.array(mxx,dtype=np.float)

        myy = getColumn(sf,4, delimiter=',', magnaprobe=False)
        myy = np.array(myy,dtype=np.float)
                
        loc = sf.split('-')[-4]
        print(loc)
        
        if loc in locs:
            #some correction shifts
            #this shifts will make the GEM-2 and MP tracks fit together better
            if date == '20210505': #P4
                mxx = mxx-15
                myy = myy+5
                
            if date == '20210508': #P5
                mxx = mxx+33
                myy = myy-2   
                
            if date == '20210510': #P6
                mxx = mxx+20
                myy = myy+28
                
            if date == '20210513': #P7
                if loc == 'P7a':
                    mxx = mxx-30
                    myy = myy-18
                if loc == 'P7b':
                    mxx = mxx-28
                    myy = myy-25
                
            #save all these corrected coordinates
            time = getColumn(sf,0, delimiter=',', magnaprobe=False)
            lon = getColumn(sf,1, delimiter=',', magnaprobe=False)
            lat = getColumn(sf,2, delimiter=',', magnaprobe=False)
            
            tt = [time,lon,lat,mxx,myy]
            table = list(zip(*tt))

            corr_fname = sf.split('.csv')[0]+'_corr.csv'
            print(corr_fname)
            with open(corr_fname, 'wb') as f:
                np.savetxt(f, table, fmt="%s", delimiter=",")
            
            #stats
            dx = mxx[1:]-mxx[:-1]
            dy = myy[1:]-myy[:-1]
            d = np.sum(np.sqrt(dx**2+dy**2))
            print('transect length:')
            print(d)
            print('MP measurement spacing:')
            spacing = np.mean(np.sqrt(dx**2+dy**2))
            print(spacing)
            mp_spacing.append(spacing)

            dtot_mp = dtot_mp+d
            n_mp = n_mp+ len(mxx)
            
            #plot MP tracks
            #dont plot the broken ones
            #if date == '20200406': continue
            plt.plot(mxx,myy,'o',ms=1,label='magnaprobe '+date+' '+loc)

    #plot GEM-tracks
    #dont plot the broken ones
    #if date == '20200406': continue
    plt.plot(xx,yy,'o',ms=1,label='GEM-2 '+date+' '+loc)
    
plt.legend(loc='upper right',ncol=1)
plt.gca().set_aspect('equal')
plt.grid()

print('total GEM-2 transect distance:')
print(dtot)
print('total MP transect distance:')
print(dtot_mp)
print('total number of MP measurements:')
print(n_mp)

print(mp_spacing)
mp_spacing_m = np.mean(np.array(mp_spacing))
print('average MP spacing:')
print(mp_spacing_m)

if loc == 'P4':
    t = 'average MP spacing: '+str(np.round(mp_spacing_m,2))+' m'
    plt.text(-160, -50, t, ha='left', wrap=True)

    t = 'total MP transect distance:: '+str(np.round(dtot_mp,2))+' m'
    plt.text(-160, -40, t, ha='left', wrap=True)

else:
    t = 'average MP spacing: '+str(np.round(mp_spacing_m,2))+' m'
    plt.text(0, -200, t, ha='left', wrap=True)

    t = 'total MP transect distance:: '+str(np.round(dtot_mp,2))+' m'
    plt.text(0, -180, t, ha='left', wrap=True)

fig1.savefig(outpath+'track_'+loc+'.png',bbox_inches='tight')
