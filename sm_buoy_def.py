import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from glob import glob
from scipy.spatial import ConvexHull, Delaunay
import pandas as pd

from tt_func import getColumn,deformation

inpath = '../data/mosaic_buoy_data/selection/'

#flist= glob(inpath+'2019P*_locs.csv')

#buoys alive all winter and inside 10km radius of PS (verified by sm_buoy_map.py)
#P103,P151,P158,P159,P193,P195,P199,P201,P204
flist = glob(inpath+'2019P103*_locs.csv')+\
    glob(inpath+'2019P151*_locs.csv')+\
    glob(inpath+'2019P158*_locs.csv')+\
    glob(inpath+'2019P159*_locs.csv')+\
    glob(inpath+'2019P193*_locs.csv')+\
    glob(inpath+'2019P195*_locs.csv')+\
    glob(inpath+'2019P199*_locs.csv')+\
    glob(inpath+'2019P201*_locs.csv')+\
    glob(inpath+'2019P204*_locs.csv')

#just best 4 bouys (distance 4-5km from PS)
flist = glob(inpath+'2019P103*_locs.csv')+\
    glob(inpath+'2019P193*_locs.csv')+\
    glob(inpath+'2019P195*_locs.csv')+\
    glob(inpath+'2019P204*_locs.csv')

##alternative 4 bouys (variable distance 1-5km from PS)
#flist = glob(inpath+'2019P158*_locs.csv')+\
    #glob(inpath+'2019P201*_locs.csv')+\
    #glob(inpath+'2019P204*_locs.csv')+\
    #glob(inpath+'2019P193*_locs.csv')

#flist = glob(inpath+'2019P103*_locs.csv')+\
    #glob(inpath+'2019P193*_locs.csv')+\
    #glob(inpath+'2019P195*_locs.csv')+\
    #glob(inpath+'2019P204*_locs.csv')+\
    #glob(inpath+'2019P158*_locs.csv')

#flist = glob(inpath+'2019P103*_locs.csv')+\
    #glob(inpath+'2019P193*_locs.csv')+\
    #glob(inpath+'2019P201*_locs.csv')+\
    #glob(inpath+'2019P204*_locs.csv')

print(flist)

plot_check=False
minang_val = 15
area_scale = [2000,20000]
min_trinum = 2
interval=3      #3h-data for SnowModel defomation proxy

#get the dates
time = getColumn(flist[0],0)
dt = [ datetime.strptime(time[x], "%Y-%m-%d %H:%M:%S") for x in range(len(time)) ][::interval]

#make an empty array for all the buoy data
data = np.zeros((len(dt),4,len(flist)))

#open all files and store all the buoy data in one array
i=0
for buoy in flist:
    print(buoy)

    x = np.asarray(getColumn(buoy,3),dtype=float)[::interval]
    y = np.asarray(getColumn(buoy,4),dtype=float)[::interval]
    u = np.asarray(getColumn(buoy,5),dtype=float)[::interval]
    v = np.asarray(getColumn(buoy,6),dtype=float)[::interval]
    
    if interval>1:
        #recalculate velocities
        #get displacements and velocities
        dx = x[1:]-x[:-1]
        dy = y[1:]-y[:-1]
        dt64 = np.array(dt, dtype='datetime64[s]')
        ddt = dt64[1:]-dt64[:-1]
        ddt = np.array(ddt, dtype='float64')       
        u = dx/ddt
        v = dy/ddt
        
        #add a zero to make the velocity vector same long as coordinates
        u = np.append(([0]),u)
        v = np.append(([0]),v)
        
        #fill masked values in x[1:] and x[:-1] by 0!
        mask = (x==0) | (np.append(([0]),x[:-1]==0))
        u=np.ma.array(u,mask=mask,fill_value=0).filled()
        v=np.ma.array(v,mask=mask,fill_value=0).filled()
        print(np.max(v))
    
    #mask everthing where v==0 (dummy value)
    data[:,0,i] = np.ma.array(x,mask=v==0,fill_value=0).filled()
    data[:,1,i] = np.ma.array(y,mask=v==0,fill_value=0).filled()
    data[:,2,i] = np.ma.array(u,mask=v==0,fill_value=0).filled()
    data[:,3,i] = np.ma.array(v,mask=v==0,fill_value=0).filled()
    
    i=i+1

    del x,y,u,v

mask=(data==0)|(np.isnan(data))|(~(np.isfinite(data)))
data = np.ma.array(data,mask=mask)
#print(data)

#empty lists to collect the values for time series
td_list=[]
div_list=[]
shr_list=[]
ls_list=[]
trinum_list=[]
date_list=[]

#for each time step
for k in range(0,data.shape[0]):
    print('******************************************************************************************k:',k)
    #triangulate all the positions
    #get the x and y coordinates, skip the masked values and fit them into pairs
    pts = data[k,:2,:].T.compressed().reshape(-1,2)

    #skip the time steps with less than 3 points
    if pts.shape[0] < 3: continue

    #velocities
    u = data[k,2,:].compressed()
    v = data[k,3,:].compressed()

    if u.shape!=data[k,0,:].compressed().shape:
        print('this will be a problem!'); continue

    #triangulation
    tri = Delaunay(pts)
    
    tripts = pts[tri.simplices]
    upts = u[tri.simplices]
    vpts = v[tri.simplices]
    trin = len(tripts)
    
    #plot the triangles every 100 steps
    if k%100.==0 and plot_check:
        plt.title(dt[k])
        plt.triplot(pts[:,0], pts[:,1], tri.simplices.copy())
        plt.plot(pts[:,0], pts[:,1], 'o')
        plt.show()
    
    td_tri = []
    ls_tri = []
    div_tri = []
    shr_tri = []
  
    ##for each triangle
    for t in range(0,trin):
        #vertices
        vert = tripts[t]
        uvert = upts[t]
        vvert = vpts[t]
        
        #sorting the vertices so that they are always counter-clockwise
        hull = ConvexHull(vert)
        vert = vert[hull.vertices]
        uvert = uvert[hull.vertices]
        vvert = vvert[hull.vertices]
    
        #calculate deformation
        a,b,c,d,minang,area=deformation(vert,uvert,vvert)
        
        #get rid of acute triangles
        mask=minang<minang_val
        a=np.ma.array(a,mask=mask).compressed()
        b=np.ma.array(b,mask=mask).compressed()
        c=np.ma.array(c,mask=mask).compressed()
        d=np.ma.array(d,mask=mask).compressed()
        area=np.ma.array(area,mask=mask).compressed()
        
        #get rid of too large and too small triangles
        ls = np.sqrt(area)
        mask=(ls<area_scale[0])|(ls>area_scale[1])
        a=np.ma.array(a,mask=mask).compressed()
        b=np.ma.array(b,mask=mask).compressed()
        c=np.ma.array(c,mask=mask).compressed()
        d=np.ma.array(d,mask=mask).compressed() 
        
        #get divergence, shear and total deformation for each triangle
        ddd = a + d
        sss = .5*np.sqrt((a-d)**2+(b+c)**2)
        td = np.sqrt(ddd**2+sss**2)
        
        td_tri.append(td)
        ls_tri.append(ls)
        div_tri.append(ddd)
        shr_tri.append(sss)
    
    #get mean values for all triangles
    tdm=np.mean(td_tri)
    lsm=np.mean(ls_tri)
    dm = np.mean(div_tri)
    sm = np.mean(shr_tri)
    trinum=len(td_tri)
        
    if tdm>0:
        td_list.append(tdm)
        div_list.append(dm)
        shr_list.append(sm)
        ls_list.append(lsm)
        trinum_list.append(trinum)
        date_list.append(dt[k])

#only keep time steps with sufficient triangle number
mask = np.array(trinum_list) < min_trinum
date_list = np.ma.array(date_list,mask=mask).compressed()
td_list = np.ma.array(td_list,mask=mask).compressed()
div_list = np.ma.array(div_list,mask=mask).compressed()
shr_list = np.ma.array(shr_list,mask=mask).compressed()
ls_list = np.ma.array(ls_list,mask=mask).compressed()
trinum_list = np.ma.array(trinum_list,mask=mask).compressed()

#make the full 3h time series for the SnowModel
#calculate area change rates for the lead/ridge-snow sink formation proxy
pos = {'ls': ls_list,
       'td': td_list,
       'divergence': div_list}

df = pd.DataFrame(data=pos,index=date_list)
#sums = df.resample('3H').mean().asfreq('3H')
#take the last value in interval
sums = df.resample('3H', convention='end').asfreq() #this is already 3-hr time series, so there will be no difference with sums!

#interpolation of nans
sums=sums.interpolate(method='polynomial',order=1)  #second order polynomial gives nagative values in TD!


print(sums)

#keep values
ls = sums.ls.values
td = sums.td.values*3600*24           #scale from s-1 to day-1
div = sums.divergence.values*3600*24
dates = sums.index.values

#convert back to datetime list
dt = dates.astype('O')
dt = [ datetime.utcfromtimestamp(x/1e9) for x in dt ]

#the position data from one of the buoys is noisy in December (15% area change is not possible!): 17-30 Dec 2019
#contrain that data and put missing values to un-realistic data
mask=(dates>np.array(datetime(2019,12,17,22),dtype='datetime64[s]')) & (dates<np.array(datetime(2019,12,29,18),dtype='datetime64[s]')) & (np.abs(ls)>11100)
mask_keep = (dates>np.array(datetime(2019,12,17,22),dtype='datetime64[s]')) & (dates<np.array(datetime(2019,12,29,18),dtype='datetime64[s]')) & (np.abs(ls)<11100)

mean_dec = np.mean(np.ma.array(ls,mask=~mask_keep))
ls=np.ma.array(ls,mask=mask,fill_value=mean_dec).filled()

#calculate area change rates
dls = ls[1:]-ls[:-1]

#add a zero to make the velocity vector same long as coordinates
dls = np.append(([0]),dls)

#fix nans that were caused by division by zero in previous step
dls = np.ma.fix_invalid(dls,fill_value=0)

#make them relative to the area size
#inside this area change are both ridges and leads, both are snow sinks and they cant be separated by such simple method (triangles only give average situation)
dls = dls/ls

#preview plots
#compare to the original time series
plt.plot(date_list,ls_list,label='Area - calculated')
plt.plot(dt,ls,label='Area - interpolated/corrected')
plt.legend()
plt.show()

plt.plot(dt,div,label='divergence (day-1)')
plt.plot(dt,dls*10,label='area change (fraction*10) 0.1=1%')
plt.plot(dt,np.zeros_like(td),'--k',lw=1)
plt.legend()
plt.show()

plt.plot(dt,div,label='divergence')
plt.plot(dt,td,label='total deformation')
plt.plot(dt,np.zeros_like(td),'--k',lw=1)
plt.legend()
plt.show()

#round for saving
ls=np.round(ls,4)
dls=np.round(dls,4)
div=np.round(div,4)
td=np.round(td,4)

#prepare output for SnowModel
year = [ datetime.strftime(x, "%Y") for x in dt ]
month = [ datetime.strftime(x, "%m") for x in dt ]
day = [ datetime.strftime(x, "%d") for x in dt ]
hour = [ datetime.strftime(x, "%H") for x in dt ]

#time series text file exports
tt = [year,month,day,hour,ls,dls,div,td]
table = list(zip(*tt))

#save output
outfile = inpath+'Deformation_3hr.csv'
#outfile = inpath+'Deformation_3hr_alternative.csv'
print(outfile)

with open(outfile, 'wb') as f:
    #header
    f.write(b'year,month,day,hour,area-length scale (m), area change rate (fraction/3h), divergence*1e6 (day^-1), total deformation*1e6 (day^-1)\n')
    np.savetxt(f, table, fmt="%s", delimiter=",")


#What snow SWE increase/decrease can be explained by deformation/blowing snow/snowfall

divergence = np.ma.array(div,mask=div<0)
convergence = np.abs(np.ma.array(div,mask=div>0))

#plot cumulative deformation and cummlative precipitation
pfile ='../data/weather_Matrosov/mosaic-snowfall/precipitation_ARM_Matrosov_3h.csv'
year = np.array(getColumn(pfile,0),dtype=int)
month = np.array(getColumn(pfile,1),dtype=int)
day = np.array(getColumn(pfile,2),dtype=int)
hour = np.array(getColumn(pfile,3),dtype=int)
pdate = [ datetime(year[x],month[x],day[x],hour[x]) for x in range(0,len(year)) ]

precip = np.array(getColumn(pfile,6),dtype=float)
precip = np.ma.array(precip,mask=precip==-9999)

#get measured snow depth from transects
ifile='../data/MCS/MP/SnowModel_Sloop_level_melt_swe.csv'
year = np.array(getColumn(ifile,0),dtype=int)
month = np.array(getColumn(ifile,1),dtype=int)
day = np.array(getColumn(ifile,2),dtype=int)
idate = [ datetime(year[x],month[x],day[x]) for x in range(0,len(year)) ]

swe = np.array(getColumn(ifile,9),dtype=float)  *1000 #convert from m to mm

#get wind speed
fname = '../data/weather/weather_Oct-Jul.csv'
wdate = getColumn(fname,0, delimiter=',')
wdate = [ datetime.strptime(x, '%Y/%m/%d %H:%M:%S') for x in wdate ]
wind = getColumn(fname,7, delimiter=',')
wind = np.array(wind,dtype=np.float)

from scipy.signal import savgol_filter
polyorder=3
window=231
wind = savgol_filter(wind, window, polyorder)


#Plotting
plt.plot(pdate,np.cumsum(precip),label='cumulative snowfall')
#plt.plot(dt,td*100,label='total deformation')
plt.plot(dt,np.cumsum(td)*2,label='cum total deformation*5')
#plt.plot(dt,np.cumsum(divergence)*10,label='cum divergence*10')
#plt.plot(dt,np.cumsum(convergence)*10,label='cum convergence*10')

#plt.plot(dt,np.cumsum(convergence)-np.cumsum(divergence),label='cum div diff')

#plt.plot(dt,ls/100,label='Area - interpolated/corrected')

plt.scatter(idate,swe,marker='x',c='r',label='SWE on level ice')

plt.plot(wdate,wind*5,label='wind speed*10')

plt.xlim(datetime(2019,10,1),datetime(2020,5,31))
plt.legend()
plt.show()


#accumulated deformation over 1 week


#accummulated convergence


#accummulated divergence



