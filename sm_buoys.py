import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from glob import glob
from pyproj import Proj, transform
import pandas as pd
from tt_func import getColumn

inpath = '../data/mosaic_buoy_data/selection/'

#SnowModel
start=datetime(2019,10,5,0,0,0)
end=datetime(2020,5,31,1,0,0,0)
fname_end = 'locs.csv'

##CO1
#start=datetime(2019,10,30,0,0,0)
#end=datetime(2020,5,7,1,0,0,0)
#fname_end = 'co1.csv'

##CO2
#start=datetime(2020,6,17,0,0,0)
#end=datetime(2020,7,31,1,0,0,0)
#fname_end = 'co2.csv'

#CO3
start=datetime(2020,8,21,0,0,0)
end=datetime(2020,9,19,1,0,0,0)
fname_end = 'co3.csv'

#buoys
fnames = sorted(glob(inpath+'2019P*_proc.csv'))
fnames = sorted(glob(inpath+'2019P103*_proc.csv')) #for co1, co2
fnames = sorted(glob('../data/mosaic_buoy_data/original/2020P237*_proc.csv')) #for co3
for fname in fnames:
    print(fname)
    #header:time,latitude (deg),longitude (deg),time_aux,time_GPSaux,barometric_pressure (hPa),battery_voltage (V),humidity_internal (%),temperature_internal (degC)
    date = getColumn(fname,0)
    dt = [ datetime.strptime(date[x], "%Y-%m-%dT%H:%M:%S") for x in range(len(date)) ]
    lon = getColumn(fname,2)
    lon = np.array(lon,dtype=np.float)
    lat = getColumn(fname,1)
    lat = np.array(lat,dtype=np.float)
    
    #take only data at full hour
    full_hour= np.where(np.array([ x.minute for x in dt ])==0,0,1)
    print(full_hour)
    
    dt = np.ma.array(dt,mask=full_hour).compressed()
    lon = np.ma.array(lon,mask=full_hour).compressed()
    lat = np.ma.array(lat,mask=full_hour).compressed()
    print(lon)
        
    #cut off any data before MOSAiC deployments and after end of winter
    si = np.argmin(abs(np.asarray(dt)-start))
    ei = np.argmin(abs(np.asarray(dt)-end))
    dt = dt[si:ei]
    lon = lon[si:ei]
    lat = lat[si:ei]
    
    #extend the time series to start on a fixed starting date: 5/10/2019
    dt = np.append(([start]),dt)
    lon = np.append(([0]),lon)
    lat = np.append(([0]),lat)
    
    #add the final date for the case if the buoy did not live that long
    dt = np.append(dt,([end]))
    lon = np.append(lon,([0]))
    lat = np.append(lat,([0]))
    
    #fill in dummy values for missing hours
    #make time series of 1-h sums
    valid = lat+1000
    pos = {'lon': lon,
           'lat': lat,
           'valid': valid}

    df = pd.DataFrame(data=pos,index=dt)
    sums = df.resample('1H').sum().asfreq('1H')
    print(sums)

    #keep values
    lon = sums.lon.values
    lat = sums.lat.values
    valid = sums.valid.values
    dates = sums.index.values

    lon=np.ma.array(lon,mask=valid<1000,fill_value=0).filled()
    lat=np.ma.array(lat,mask=valid<1000,fill_value=0).filled()
    
    #convert back to datetime list
    dt = dates.astype('O')
    dt = [ datetime.utcfromtimestamp(x/1e9) for x in dt ]

    #calculate geographical coordinates
    inProj = Proj(init='epsg:4326')
    outProj = Proj('+proj=stere +lat_0=%f +lon_0=%f +x_0=0 +y_0=0 +ellps=WGS84'%(0,75))
    x,y = transform(inProj,outProj,lon,lat)
    
    #x gets calculated from 0,0 position, remove those
    x=np.ma.array(x,mask=lat==0,fill_value=0).filled()
    
    #get displacements and velocities
    dx = x[1:]-x[:-1]
    dy = y[1:]-y[:-1]
    dt64 = np.array(dt, dtype='datetime64[s]')
    ddt = dt64[1:]-dt64[:-1]
    ddt = np.array(ddt, dtype='float64')
    #hourly displacements, should be 3600 seconds!
    #print(ddt)
    
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
 
    #save the locations to individual files
    file_name = fname.split('proc')[0]+fname_end
    print(file_name)
    
    tt = [dt,lon,lat,x,y,u,v]
    table = list(zip(*tt))

    with open(file_name, 'wb') as f:
        #header
        f.write(b'date/time,lon,lat,x,y,u (m/s),v (m/s)\n')
        np.savetxt(f, table, fmt="%s", delimiter=",")


#cp ../data/mosaic_buoy_data/original/*co3.csv ../data/mosaic_buoy_data/selection/2020P237_300234068818610_co3.csv
