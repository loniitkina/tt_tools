import numpy as np
from glob import glob
from tt_func import getColumn
import matplotlib.pyplot as plt

#manually find the best overlay between the tracks - different for each date






inpath = '../../../MOSAiC/thickness_workspace/01-ice-thickness/'
inpath_mp = '../data/'
outpath = '../plots/'

#plot
fig1 = plt.figure(figsize=(12,10))

#all the files
flist = glob(inpath+'/*PS122-2*/mosaic-transect-*-gem2-556-track-icecs-xy.csv')
flist.sort()

dtot = 0
dtot_mp = 0

for i in flist:
    fname = i
    print(fname)
    
    date = fname.split('/')[-1].split('-')[2]
    if date == '20200116': continue     #there is something wrong with the coordinted for this date - was supposed to be a regular transect day (good data)
    if date == '20200123': continue     #long transect
    #if (date != '20191226') and (date != '20191219'): continue   #problematic transects, combine both
    #if (date != '20200112') and (date != '20191222') and (date != '20200207') and (date != '20200126'): continue     #snow1 transects, currently gem data from 20200112 and 20200207 not processed
    #if (date != '20200123'): continue

    outname = 'gem2_tracks_'+date+'.png'
    
    print(fname)
    xx = getColumn(inpath+fname,3, delimiter=',', magnaprobe=False)
    xx = np.array(xx,dtype=np.float)

    yy = getColumn(inpath+fname,4, delimiter=',', magnaprobe=False)
    yy = np.array(yy,dtype=np.float)
    
    dx = xx[1:]-xx[:-1]
    dy = yy[1:]-yy[:-1]
    d = np.sum(np.sqrt(dx**2+dy**2))
    print('transect length:')
    print(d)
    print('GEM-2 measurement spacing:')
    spacing = np.mean(np.sqrt(dx**2+dy**2))
    print(spacing)

    dtot = dtot+d
    
    mp_list = glob(inpath_mp+date+'*_transect_track-icecs-xy.csv')
    for sf in mp_list:
        mxx = getColumn(sf,3, delimiter=',', magnaprobe=False)
        mxx = np.array(mxx,dtype=np.float)

        myy = getColumn(sf,4, delimiter=',', magnaprobe=False)
        myy = np.array(myy,dtype=np.float)
        
        loc = sf.split('/')[-1].split('_')[1]
        print(loc)
        
        #some correction factors
        if date == '20200220':
            mxx = mxx-10
            
            if loc == 'Nloop':
                myy = myy-3
            
        if date == '20200102':
            mxx = mxx-7
            myy = myy-8
                
            if loc == 'Sloop':
                mxx = mxx+5
                
        if date == '20200109':
            myy = myy-4  
            
        if date == '20200126':
            myy = myy+7
        
        if date == '20200130':
            mxx = mxx+3
            
        if date == '20200206':
            mxx = mxx-5
            
        #snow1
        if date == '20191222':
            mxx = mxx+3
            myy = myy+3
            
        #long transect (ice on 3 different groups of floes moving actively and independently)
        if date == '20200123':
            print(len(mxx))
            mxx[:300] = mxx[:300]+15
            mxx[500:] = mxx[500:]-5
            #myy = myy+3
            
        dx = mxx[1:]-mxx[:-1]
        dy = myy[1:]-myy[:-1]
        d = np.sum(np.sqrt(dx**2+dy**2))
        print('transect length:')
        print(d)
        print('MP measurement spacing:')
        spacing = np.mean(np.sqrt(dx**2+dy**2))
        print(spacing)

        dtot_mp = dtot_mp+d

        
        
        plt.plot(mxx,myy,'o',ms=1)#,label=date+loc)


    plt.plot(xx,yy,'o',ms=1)#,label=date)
    
    
plt.legend()
print(outname)
fig1.savefig(outpath+outname)
fig1.savefig(outpath+'gem2+mp_tracks_CO.png')

print(dtot)
print(dtot_mp)



exit()

#print(xx)


#MP



#early date
fname = '20200102_Sloop_MP_transect_track-icecs-xy.csv'
mxx1 = getColumn(inpath+fname,3, delimiter=',', magnaprobe=False)
mxx1 = np.array(mxx1,dtype=np.float)

myy1 = getColumn(inpath+fname,4, delimiter=',', magnaprobe=False)
myy1 = np.array(myy1,dtype=np.float)


fname = '20200102_Nloop_MP_transect_track-icecs-xy.csv'
mxx2 = getColumn(inpath+fname,3, delimiter=',', magnaprobe=False)
mxx2 = np.array(mxx2,dtype=np.float)

myy2 = getColumn(inpath+fname,4, delimiter=',', magnaprobe=False)
myy2 = np.array(myy2,dtype=np.float)

#MP coordinates looks shifted to 'positive directions' - probably some drift in time between the GEM-2 and MP measurement???
#should the MP coordinates be manually corrected by some ~10 m???

mxx1 = mxx1-5
myy1 = myy1-3

mxx2 = mxx2-10
myy2 = myy2-3

#get lenght of both loops
#S loop
dx = mxx1[1:]-mxx1[:-1]
dy = myy1[1:]-myy1[:-1]
d = np.sum(np.sqrt(dx**2+dy**2))
print('S loop length:')
print(d)
print('MP measurement step:')
step = np.mean(np.sqrt(dx**2+dy**2))
print(step)

#N loop
dx = mxx2[1:]-mxx2[:-1]
dy = myy2[1:]-myy2[:-1]
d = np.sum(np.sqrt(dx**2+dy**2))
print('N loop length:')
print(d)
print('MP measurement step:')
step = np.mean(np.sqrt(dx**2+dy**2))
print(step)





##late date
#fname = '20200220_Sloop_MP_transect_track-icecs-xy.csv'
#mxx1 = getColumn(inpath+fname,3, delimiter=',', magnaprobe=False)
#mxx1 = np.array(mxx1,dtype=np.float)

#myy1 = getColumn(inpath+fname,4, delimiter=',', magnaprobe=False)
#myy1 = np.array(myy1,dtype=np.float)


#fname = '20200220_Nloop_MP_transect_track-icecs-xy.csv'
#mxx2 = getColumn(inpath+fname,3, delimiter=',', magnaprobe=False)
#mxx2 = np.array(mxx2,dtype=np.float)

#myy2 = getColumn(inpath+fname,4, delimiter=',', magnaprobe=False)
#myy2 = np.array(myy2,dtype=np.float)

##MP coordinates looks shifted to 'positive directions' - probably some drift in time between the GEM-2 and MP measurement???
##should the MP coordinates be manually corrected by some ~10 m???

#mxx1 = mxx1-10
##myy1 = myy1-5

#mxx2 = mxx2-10
#myy2 = myy2-3

##get lenght of both loops
##S loop
#dx = mxx1[1:]-mxx1[:-1]
#dy = myy1[1:]-myy1[:-1]
#d = np.sum(np.sqrt(dx**2+dy**2))
#print('S loop length:')
#print(d)
#print('MP measurement step:')
#step = np.mean(np.sqrt(dx**2+dy**2))
#print(step)

##N loop
#dx = mxx2[1:]-mxx2[:-1]
#dy = myy2[1:]-myy2[:-1]
#d = np.sum(np.sqrt(dx**2+dy**2))
#print('N loop length:')
#print(d)
#print('MP measurement step:')
#step = np.mean(np.sqrt(dx**2+dy**2))
#print(step)








#plot
fig1 = plt.figure(figsize=(12,10))


plt.plot(xx,yy,c='0.5')
#plt.plot(mxx1,myy1)
#plt.plot(mxx2,myy2)

#Lets get the values!
inpath = '../../../MOSAiC/leg2_ICE/transect/20200220/'
inpath = '../../../MOSAiC/leg2_ICE/transect/20200102/'
flist = glob(inpath+'*loop.dat')

fname = flist[0]
snod = getColumn(fname,3, delimiter=',', magnaprobe=True)
snod = np.array(snod,dtype=np.float)[:-2]
plt.scatter(mxx2,myy2,c=snod, cmap=plt.cm.Reds,vmin=0, vmax=120)

fname = flist[1]
snod = getColumn(fname,3, delimiter=',', magnaprobe=True)
snod = np.array(snod,dtype=np.float)[:-2]
plt.scatter(mxx1,myy1,c=snod, cmap=plt.cm.Reds,vmin=0, vmax=120)

plt.colorbar()

fig1.savefig(outpath+'test1.png')
