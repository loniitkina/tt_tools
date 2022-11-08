import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from datetime import datetime
from glob import glob
from tt_func import getColumn, floenavi_coords

#read in all the snowpit density data, calculate the local coordinate system location and sort by location in the CO

#get all floenavi master station records
refdate=[]
reflon=[]
reflat=[]
refhead=[]
refstat_files = sorted(glob('../data/floenavi/data_master-solution_mosaic-leg*-floenavi-refstat-v1p0.csv'))
for refstat in refstat_files:
    print(refstat)
    
    refdate.extend(getColumn(refstat,0))
    reflon.extend(getColumn(refstat,1))
    reflat.extend(getColumn(refstat,2))
    refhead.extend(getColumn(refstat,3))
    
refdt = [ datetime.strptime(refdate[x], "%Y-%m-%d %H:%M:%S") for x in range(len(refdate)) ]
reflon = np.array(reflon,dtype=np.float)
reflat = np.array(reflat,dtype=np.float)
refhead = np.array(refhead,dtype=np.float)


#SMP data processed by David Wager
fname = '../data/snowpits_wagner/swe_smpdensity_leg1_leg3_archive/swe_smp_k2020.filled.csv'
#header: Time,doid,z [m],SWE [mm],LAT,LON,location
date = getColumn(fname,0)
dt = [ datetime.strptime(date[x], "%Y-%m-%d %H:%M:%S+00:00") for x in range(len(date)) ]
doid = np.array(getColumn(fname,1))
snod = getColumn(fname,2)
snod = np.array(snod,dtype=np.float)
swe = getColumn(fname,3)
swe = np.array(swe,dtype=np.float)
lon = getColumn(fname,5)
lon = np.array(lon,dtype=np.float)
lat = getColumn(fname,4)
lat = np.array(lat,dtype=np.float)
location = np.array(getColumn(fname,6))

#group snowpits by location
locations = list(set(location))

for i in range(0,len(locations)):
    print(locations[i])
    
    #if locations[i]!='Nloop':
        #continue
    
    name = np.ma.array(location,mask=location!=locations[i])
    date_name = np.ma.array(dt,mask=name.mask).compressed()
    doid_name = np.ma.array(doid,mask=name.mask).compressed()
    snod_name = np.ma.array(snod,mask=name.mask).compressed()
    swe_name = np.ma.array(swe,mask=name.mask).compressed()
    lat_name = np.ma.array(lat,mask=name.mask).compressed()
    lon_name = np.ma.array(lon,mask=name.mask).compressed()
    
    #calculate bulk density: SWE = (rho_s/rho_w) * h_s
    rho_w = 1000
    rho_s = ((swe_name/rho_w)/snod_name)*rho_w   
    
    #calculate the local coordinates
    x_name,y_name = floenavi_coords(date_name,lat_name,lon_name,refdt,reflat,reflon,refhead)
    
    #save the locations to individual files
    file_name = fname.split('.filled')[0]+'_'+locations[i]+'.csv'
    print(file_name)
    
    tt = [date_name,doid_name,snod_name,swe_name,lat_name,lon_name,x_name,y_name,rho_s]
    table = list(zip(*tt))

    with open(file_name, 'wb') as f:
        #header
        f.write(b'Date/time,doid,z [m],SWE [mm],LAT,LON,x,y,bulk snow density [kg/m3]\n')
        np.savetxt(f, table, fmt="%s", delimiter=",")

#exit()

#SWE cylinder    
fname='../data/snowpits_amy/metadata_SWE.csv'
#header: Event,Location,Timestamp,Latitude,Longitude,SWE mm,SnowHeight cm,Comment
date = getColumn(fname,2)
dt = [ datetime.strptime(date[x], "%m/%d/%Y %H:%M") for x in range(len(date)) ]
doid = np.array(getColumn(fname,0))
snod = getColumn(fname,6)
snod = np.array(snod,dtype=np.float)/100    #convert to m
swe = getColumn(fname,5)
swe = np.array(swe,dtype=np.float)
lon = getColumn(fname,4)
lon = np.array(lon,dtype=np.float)
lat = getColumn(fname,3)
lat = np.array(lat,dtype=np.float)
location = np.array(getColumn(fname,1))
    
#group snowpits by location
locations = list(set(location))
print(locations)

for i in range(0,len(locations)):
    print(locations[i])
    
    name = np.ma.array(location,mask=location!=locations[i])
    date_name = np.ma.array(dt,mask=name.mask).compressed()
    doid_name = np.ma.array(doid,mask=name.mask).compressed()
    snod_name = np.ma.array(snod,mask=name.mask).compressed()
    swe_name = np.ma.array(swe,mask=name.mask).compressed()
    lat_name = np.ma.array(lat,mask=name.mask).compressed()
    lon_name = np.ma.array(lon,mask=name.mask).compressed()
    
    #calculate bulk density: SWE = (rho_s/rho_w) * h_s
    rho_w = 1000
    rho_s = ((swe_name/rho_w)/snod_name)*rho_w   
    
    #calculate the local coordinates
    x_name,y_name = floenavi_coords(date_name,lat_name,lon_name,refdt,reflat,reflon,refhead)
    
    #save the locations to individual files
    file_name = fname.split('.csv')[0]+'_'+locations[i]+'.csv'
    print(file_name)
    
    tt = [date_name,doid_name,snod_name,swe_name,lat_name,lon_name,x_name,y_name,rho_s]
    table = list(zip(*tt))

    with open(file_name, 'wb') as f:
        #header
        f.write(b'Date/time,doid,z [m],SWE [mm],LAT,LON,x,y,bulk snow density [kg/m3]\n')
        np.savetxt(f, table, fmt="%s", delimiter=",")

#density cutter
fname='../data/snowpits_amy/metadata_DensityCutter.csv'
#header: Event,Location,Latitude,Longitude,Timestamp,Top cm,Bottom cm,SnowDensity kgm-3,SalinityContainer,SensorScale,Comment
date = getColumn(fname,4)
dt = [ datetime.strptime(date[x], "%m/%d/%Y %H:%M") for x in range(len(date)) ]
doid = np.array(getColumn(fname,0))
lon = getColumn(fname,3)
lon = np.array(lon,dtype=np.float)
lat = getColumn(fname,2)
lat = np.array(lat,dtype=np.float)
location = np.array(getColumn(fname,1))
snod1 = getColumn(fname,5)
snod1 = np.array(snod1,dtype=np.float)/100
snod2 = getColumn(fname,6)
snod2 = np.array(snod2,dtype=np.float)/100
rho = getColumn(fname,7)
rho = np.array(rho,dtype=np.float)

    
#group snowpits by location
locations = list(set(location))
print(locations)

for i in range(0,len(locations)):
    print(locations[i])
    
    name = np.ma.array(location,mask=location!=locations[i])
    date_name = np.ma.array(dt,mask=name.mask).compressed()
    doid_name = np.ma.array(doid,mask=name.mask).compressed()
    snod1_name = np.ma.array(snod1,mask=name.mask).compressed()
    snod2_name = np.ma.array(snod2,mask=name.mask).compressed()
    rho_name = np.ma.array(rho,mask=name.mask).compressed()
    lat_name = np.ma.array(lat,mask=name.mask).compressed()
    lon_name = np.ma.array(lon,mask=name.mask).compressed()
    
    ##calculate bulk density: SWE = (rho_s/rho_w) * h_s
    #rho_w = 1000
    #rho_s = ((swe_name/rho_w)/snod_name)*rho_w   
    
    #calculate the local coordinates
    x_name,y_name = floenavi_coords(date_name,lat_name,lon_name,refdt,reflat,reflon,refhead)
    
    #save the locations to individual files
    file_name = fname.split('.csv')[0]+'_'+locations[i]+'.csv'
    print(file_name)
    
    tt = [date_name,doid_name,snod1_name,snod2_name,rho_name,lat_name,lon_name,x_name,y_name]
    table = list(zip(*tt))

    with open(file_name, 'wb') as f:
        #header
        f.write(b'Date/time,doid,z top [m], z bottom [m],snow density [kg/m3],LAT,LON,x,y\n')
        np.savetxt(f, table, fmt="%s", delimiter=",")



    
#ax.plot(rot_x,rot_y,'x',ms=5,c='r')
