import numpy as np
from glob import glob
from tt_func import getColumn
import matplotlib.pyplot as plt
from datetime import datetime



inpath = '../data/MCS/MP/'
locs = ['Nloop','Sloop','transect','combi','ridge*','snow1','runway','special','albedoRBB','albedoLD','albedoK','kuka','ARIEL','transectstbd','transectport','transectbow','transectgrid','drillholes','initialsurvey']
cols = ['b','m','m','m','g','y','c','k','hotpink','royalblue','hotpink','orange','darkred','k','k','k','k','k','k','k','k']


#Timeseries scatter plot
fig1 = plt.figure(figsize=(10,10))
fig1.patch.set_facecolor('0.5')
ax = fig1.add_subplot(211)
bx = fig1.add_subplot(212)
ax.set_ylabel('Transect Lenght (m)', fontsize=20)
bx.set_xlabel('Time', fontsize=20)
#bx.set_title(title, fontsize=25)
bx.set_ylabel('Measurement spacing (m)', fontsize=20)
bx.tick_params(axis="x", labelsize=14)
bx.tick_params(axis="y", labelsize=14)
##bx.set_facecolor('0.3')
#bx.set_xlim(0,1)
#bx.set_ylim(0,2)

total_l=0
total_n=0

for loc in range(0,len(locs)):
    #get list of all files for listed locations
    flist = sorted(glob(inpath+'*/*'+locs[loc]+'-meta.txt'))

    for fn in flist:
        print(fn)
        
        datem = fn.split('-')[-4].split('_')[0]
        date = datetime.strptime(datem, '%Y%m%d')
        
        with open(fn) as f:
            content = f.readlines()
        f.close()
        
        ll=float(content[0])
        ss=float(content[1])
        
        #GPS problem on MP
        if locs[loc] == 'snow1' and datem=='20200223':
            ll = 400.
            ss = 1.
            
        #combi
        if locs[loc]=='combi':
            print(combi)
            #here we need to manually alter the statistics...
        
        if fn != flist[0] or locs[loc]=='transectstbd' or locs[loc]=='transectbow' or locs[loc]=='transectport' or locs[loc]=='transectgrid' or locs[loc]=='drillholes' or locs[loc]=='initialsurvey':
            ax.scatter(date,ll,c=cols[loc])
        else:
            ax.scatter(date,ll,c=cols[loc],label=locs[loc])
        bx.scatter(date,ss,c=cols[loc])
        
        if locs[loc]!='combi':
            total_l = total_l+ll
            total_n = total_n+int(ll/ss)


#print total lenght of all MOSAiC transects:
print('Total lenght (km) of all MOSAiC transects')
print(total_l/1000)
print('Total number of all MOSAiC MP measurements')
print(total_n)



ax.legend(ncol=4)
fig1.autofmt_xdate()
plt.show()



#get dates from file names

#open files

#read spacing and total lenght

#plot dates vs total lenght

#plot dates vs spacings
