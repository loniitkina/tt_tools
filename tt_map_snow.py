import numpy as np
from glob import glob
from tt_func import getColumn
import matplotlib.pyplot as plt

#GEM-2
inpath = '../../../MOSAiC/thickness_workspace/01-ice-thickness/20200220-PS122-2_25-117/'
outpath = '../plots/'

fname = 'mosaic-transect-20200220-gem2-556-track-icecs-xy.csv'
xx = getColumn(inpath+fname,3, delimiter=',', magnaprobe=False)
xx = np.array(xx,dtype=np.float)

yy = getColumn(inpath+fname,4, delimiter=',', magnaprobe=False)
yy = np.array(yy,dtype=np.float)


#print(xx)


#MP
inpath = '../data/'
outpath = '../plots/'

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
