import numpy as np
from glob import glob
from tt_func import getColumn
import matplotlib.pyplot as plt

#manually find the best overlay between the GEM-2 and MP tracks - different for each date
#take GEM-2 position as the better one and adjust MP to it

#also shift lateraly whole transects relativelly to the selected fixed date

#how to account for rotation???

#save file with shifted x,y coordinates






#inpath = '../../../MOSAiC/thickness_workspace/01-ice-thickness/'
inpath = '../data/MCS/GEM2_thickness/01-ice-thickness/'

#inpath_mp = '../data/'
inpath_mp = '../data/MCS/MP/'

#outpath = '../plots/'
outpath = '../plots_AGU/'

#limit location-wise
locs = ['Nloop','Sloop']
locs = ['Sloop']
locs = ['Nloop']


#plot
fig1 = plt.figure(figsize=(12,10))

#all the files
flist = glob(inpath+'*PS122-3*/mosaic-transect-*-gem2-556-track-icecs-xy.csv')
flist.sort()

dtot = 0
dtot_mp = 0
n_mp = 0
mp_spacing=[]

for i in flist:
    #if i !=flist[12]: continue
    fname = i
    print(fname)
    
    date = fname.split('/')[-1].split('-')[2]
    if date == '20191024': continue     #Nloop has partially different track here
    if date == '20191031': continue     #Nloop has partially different track here
    if date == '20200116': continue     #there is something wrong with the GEM-2 coordintes for this date - was supposed to be a regular transect day (good data)
    if date == '20200123': continue     #long transect
    if date == '20200403': continue     #bad MP coordinate conversion
    
    print(fname)
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
                
        loc = sf.split('_')[-1].split('-')[0]
        print(loc)
        
        if loc in locs:
            
            #The tru position is Sloop on 20191205
            
            #some correction shifts
            #this shifts will make the GEM-2 and MP tracks fit together better
            #leg1
            if date == '20191024':
                mxx = mxx+7
                myy = myy-2
            
            if date == '20191031':
                mxx = mxx+5
                myy = myy-2
            
            if date == '20191107':
                mxx = mxx+2
                myy = myy+2
                
            if date == '20191114':
                myy = myy-2
                
            if date == '20191121':
                mxx = mxx-3
                myy = myy+3
            
            if date == '20191128':
                mxx = mxx+6
                myy = myy+4
                
            if date == '20191205':
                mxx = mxx-10
                myy = myy-5
            
            #leg2:
            if date == '20191219':  #this is a bad fit and it will probably not work
                mxx = mxx-600
                myy = myy-450
                
            if date == '20191226':  #most of Sloop GEM-2 data is missing
                
                #mixed up coordinates in '20191226'
                if loc == 'Sloop':
                    tmp1=mxx.copy();tmp2=myy.copy()
                    mxx = -tmp2
                    myy = tmp1
                    myy = myy-60
                    mxx = mxx-73
                    
                mxx = mxx-590
                myy = myy-438
                

            #if date == '20200102':
                #mxx = mxx-7
                #myy = myy-8
            
            if date == '20200109':
                mxx = mxx+5
                
                ##now also shift MP and GEM-2 positions to better fit the location on 20191205
                #mxx = mxx+25
                #myy = myy+10


            if date == '20200130':
                mxx = mxx-4
                myy = myy+4
            
            if date == '20200206':
                mxx = mxx-0
                myy = myy-4
                
                ##now also shift MP and GEM-2 positions to better fit the location on 20191205
                #mxx = mxx+20
                #myy = myy-10
                
                #xx = xx+20
                #yy = yy-10
            
            if date == '20200220':
                mxx = mxx+4
                myy = myy-12
                                    
                ##now also shift MP and GEM-2 positions to better fit the location on 20191205
                #mxx = mxx+25
                #myy = myy-15
                
                #xx = xx+20
                #yy = yy-20
            
            #leg3:
            if date == '20200227':      #part of N loop is missing
                mxx = mxx+8
                myy = myy-1
            
            if date == '20200305':      
                mxx = mxx+0
                myy = myy-0   
            
            if date == '20200326':      
                mxx = mxx+11
                myy = myy+3
            
            if date == '20200330':      
                mxx = mxx+1
                myy = myy+1
                
            if date == '20200406':      #MP loop is broken up in two pieces, needs fixing... OK for PDF
                mxx = mxx+5
                myy = myy+2  
                
            if date == '20200416':      #GPS failure on GEM-2, no coordinates
                mxx = mxx+0
                myy = myy+0
            
            if date == '20200424':     
                mxx = mxx+5
                myy = myy-1
            
            if date == '20200426':     
                mxx = mxx+3
                myy = myy+1
                
            if date == '20200430':     
                mxx = mxx+4
                myy = myy+3   
                
            ##snow1
            #if date == '20191222':
                #mxx = mxx+3
                #myy = myy+3
                
            ##long transect (ice on 3 different groups of floes moving actively and independently)
            #if date == '20200123':
                #print(len(mxx))
                #mxx[:300] = mxx[:300]+15
                #mxx[500:] = mxx[500:]-5
                ##myy = myy+3
                
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
            if date == '20200406': continue
            #plt.plot(mxx,myy,'o',ms=1,label=date+loc)

    #plot GEM-tracks
    #dont plot the broken ones
    if date == '20200406': continue
    #plt.plot(xxc,yyc,'o',ms=1,label=date)
    plt.plot(xx,yy,'o',ms=1,label=date)
    
plt.legend()
plt.gca().set_aspect('equal')
plt.grid()
#outname = 'gem2_tracks_'+date+'.png'
#print(outname)
#fig1.savefig(outpath+outname)
fig1.savefig(outpath+'track_test.png')
#fig1.savefig(outpath+'deformation_both_loops.png')
#fig1.savefig(outpath+'track_gem2+mp_CO.png')

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


## print-outs from all CO (currently available, some missing from leg 3), without additional measurements on the roads with MP (leg 1)
#total GEM-2 transect distance:
#96767.79635714383
#total MP transect distance:
#62484.54571565336
#total number of MP measurements:
#35375
#[2.213803973719773, 2.0652795886166753, 2.1835839414416722, 3.173571701446952, 2.479780055045009, 2.935324116207668, 2.2538389545601016, 2.5347212396355197, 2.7183011709776204, 1.8089892400278789, 2.1704933776638464, 1.873036402749838, 1.873036402749838, 1.7020857834755088, 1.038846315366049, 1.394629460083577, 1.3962575069064833, 1.0419229257121831, 1.3931097818806129, 1.9285354297045696, 1.0754161183593833, 0.8658997785608737, 1.1852216519369592, 1.053777465311667, 1.6240264079942175, 1.0166425709856537, 1.2153444759899679, 1.0645152662498005, 0.9206570819614966, 1.0185994442032569, 1.057452012149723, 1.0509275879537878, 1.0312457549180107, 1.0379463371039965, 1.0565063661036724, 1.027466507882035, 1.0423393490491404, 1.027466507882035, 1.0423393490491404, 27.137770424730718, 1.061024633847217, 1.1787117837757906, 1.125291314944368, 1.0182621049031575, 1.0401132261092245, 1.125291314944368, 1.0182621049031575, 1.0401132261092245, 2.5044744079029826, 1.0313547499661229, 1.591474198808047, 2.5044744079029826, 1.0313547499661229, 1.591474198808047, 2.5044744079029826, 1.0313547499661229, 1.591474198808047, 1.6199026011125897, 1.6199026011125897, 1.4993463225489694, 1.6248706988443162, 1.6218552692012207, 1.3582501724228833, 1.2878698891745015, 1.372437912643837]
#average MP spacing:
#1.9034480472765505
